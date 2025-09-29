import functools
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import swapi.utils
from django.db import Error as DBError
from django.db import close_old_connections, connection, transaction
from requests.exceptions import RequestException
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from . import clients, constants, models, utils


def determine_max_worker_units():
    """
    Determine the maximum number of worker units that can be safely used 
    based on the database's connection limits.

    The function calculates half of the maximum PostgreSQL connections 
    available (to leave room for other operations) and caps the result 
    at a fixed threshold of workers to avoid oversubscription.

    Returns:
        int: The maximum number of worker units allowed.
    """
    threshold = 50
    return min(swapi.utils.get_postgres_max_connections() // 2, threshold)


def clear_tables():
    """
    Truncate application tables to start with a clean database state.

    This operation is performed directly at the database level for 
    better performance than deleting rows through the ORM.

    - RESTART IDENTITY: Resets sequences for all truncated tables.
    - CASCADE: Ensures dependent tables are also truncated.

    Tables truncated:
        - StagedRelationship
        - Film
        - Character
        - Starship
    """
    db_models = [
        models.StagedRelationship,
        models.Film,
        models.Character,
        models.Starship,
    ]
    for model in db_models:
        model.objects.truncate(cascade=True)


class SWAPIResourceManager:
    """
    Base manager for handling ingestion of SWAPI resources.

    Provides a template for fetching data from SWAPI, validating it,
    persisting entity rows in the database, and staging many-to-many
    relationships for later bulk insertion into through tables.

    Subclasses must define:
        - entity_model: Django model representing the resource.
        - resource_url: Base URL of the SWAPI endpoint for this resource.
        - resource_enum: Enum value representing this resource type.
        - related_resource_enum: Enum value for the related resource type.
        - total_resource_items: Total number of resources (for pagination).
    """
    entity_model = None
    entity_fields = []
    resource_url = None
    resource_enum = None
    related_resource_enum = None
    total_resource_items = None
    staged_relationship_table = models.StagedRelationship

    def __init__(self, page, serializer):
        """
        Initialize a manager for a specific resource page.

        Args:
            page (int): Page number of the resource batch.
            serializer (Serializer): DRF serializer used for validation.
        """
        self.entity_fields = self.entity_model.get_deserialized_fields()
        self.page = page
        self.serializer = serializer

    @classmethod
    def pages_count(cls):
        """
        Compute the number of pages for this resource.

        Returns:
            int: Total page count based on `total_resource_items`
                 and configured `PAGE_SIZE`.
        """
        quotient = cls.total_resource_items // constants.PAGE_SIZE
        if not cls.total_resource_items % constants.PAGE_SIZE:
            return quotient
        return quotient + 1

    def batch_fetch_and_validate_resource_data(self):
        """
        Fetch and validate a batch of resource data from SWAPI.

        The response data is validated against the provided serializer.
        Any validation errors are re-raised with the offending payload.

        Raises:
            ValidationError: If validation fails, including details of
                             which records caused errors.

        Returns:
            list[dict]: Validated resource data ready for persistence.
        """
        page_url = f"{self.resource_url}?page={self.page}"
        fetched_data = clients.get_swapi_data(page_url)
        serializer_instance = self.serializer(data=fetched_data, many=True)
        try:
            serializer_instance.is_valid(raise_exception=True)
        except ValidationError as e:
            error_message = [
                {"data": data, "error": error}
                for data, error in zip(fetched_data, e.detail)
                if error
            ]
            raise ValidationError(error_message)
        return serializer_instance.validated_data

    def batch_create_entities(self, batch_validated_data):
        """
        Bulk insert entity rows for this resource.

        Args:
            batch_validated_data (list[dict]): Validated resource data.

        Notes:
            Uses `bulk_create` for performance. Does not trigger model
            `save()` hooks or signals.
        """
        entities_to_create = []

        for resource_data in batch_validated_data:
            entity = self.entity_model(
                **{field: resource_data.get(field) for field in self.entity_fields}
            )
            entities_to_create.append(entity)

        self.entity_model.objects.bulk_create(entities_to_create)

    def batch_create_staged_relationships(self, batch_validated_data):
        """
        Bulk insert staged relationships for this resource batch.

        Relationships are stored in a temporary "staged" table, mapping
        from SWAPI IDs to related SWAPI IDs. These are later resolved
        to actual database IDs during through-table population.

        Args:
            batch_validated_data (list[dict]): Validated resource data.
        """
        staged_relationships_to_create = []
        for resource_data in batch_validated_data:
            related_resources_urls = resource_data.get(
                self.related_resource_enum.plural, []
            )
            for related_resource_url in related_resources_urls:
                staged_relationship = self.staged_relationship_table(
                    **{
                        "from_type": self.resource_enum.value,
                        "from_swapi_id": resource_data["swapi_id"],
                        "to_type": self.related_resource_enum.value,
                        "to_swapi_id": utils.id_from_swapi_detail_url(
                            related_resource_url
                        ),
                    }
                )
                staged_relationships_to_create.append(staged_relationship)
        self.staged_relationship_table.objects.bulk_create(
            staged_relationships_to_create
        )

    @classmethod
    def batch_through_table_insert(cls):
        """
        Populate the many-to-many through table for this resource.

        Uses a raw SQL INSERT ... SELECT ... statement for efficiency.
        Only inserts relationships matching the configured
        `resource_enum` and `related_resource_enum`.

        Notes:
            - Runs at the DB level for maximum performance.
            - Skips potential duplicates via `ON CONFLICT DO NOTHING`.
            - Prints thread ID and table name on completion.
        """
        thread_id = threading.get_ident()
        staged_relationship_table_name = cls.staged_relationship_table._meta.db_table
        entity_table_name = cls.entity_model._meta.db_table
        related_entity_table_name = (
            cls.entity_model.get_many_to_many_related_model_table_name()
        )
        related_entity_many_to_many_fieldname = (
            cls.entity_model.get_many_to_many_fieldname()
        )
        through_table = getattr(
            cls.entity_model, related_entity_many_to_many_fieldname
        ).through
        through_table_name = through_table._meta.db_table
        through_table_column_names_joined = ", ".join(
            [f"{cls.resource_enum.value}_id", f"{cls.related_resource_enum.value}_id"]
        )

        with connection.cursor() as cursor:
            sql = f"""
                INSERT INTO {through_table_name} ({through_table_column_names_joined})
                SELECT from_.id, to_.id
                FROM {staged_relationship_table_name} sr
                JOIN {entity_table_name} from_ ON sr.from_swapi_id = from_.swapi_id
                JOIN {related_entity_table_name} to_ ON sr.to_swapi_id = to_.swapi_id
                WHERE sr.from_type = '{cls.resource_enum.value}' AND sr.to_type = '{cls.related_resource_enum.value}'
            """
            cursor.execute(sql)
        print(f"Thread Id: {thread_id}, [{through_table_name}] finished population")

    @transaction.atomic
    def batch_fetch_validate_store_resource_data(self):
        """
        Full pipeline for one resource batch.

        Steps:
            1. Fetch and validate data from SWAPI.
            2. Bulk insert entities into the entity table.
            3. Bulk insert staged relationships into the staging table.

        Notes:
            Runs inside a transaction to ensure atomicity.
        """
        batch_validated_data = self.batch_fetch_and_validate_resource_data()
        self.batch_create_entities(batch_validated_data)
        self.batch_create_staged_relationships(batch_validated_data)


class SWAPIFilmsManager(SWAPIResourceManager):
    entity_model = models.Film
    resource_url = constants.SWAPI_FILMS_URL
    resource_enum = constants.ResourceEnum.FILM
    related_resource_enum = constants.ResourceEnum.STARSHIP
    total_resource_items = constants.TOTAL_FILMS


class SWAPICharactersManager(SWAPIResourceManager):
    entity_model = models.Character
    resource_url = constants.SWAPI_CHARACTERS_URL
    resource_enum = constants.ResourceEnum.CHARACTER
    related_resource_enum = constants.ResourceEnum.FILM
    total_resource_items = constants.TOTAL_CHARACTERS


class SWAPIStarshipsManager(SWAPIResourceManager):
    entity_model = models.Starship
    resource_url = constants.SWAPI_STARSHIPS_URL
    resource_enum = constants.ResourceEnum.STARSHIP
    related_resource_enum = constants.ResourceEnum.CHARACTER
    total_resource_items = constants.TOTAL_STARSHIPS


def run_manager_for_page(manager_cls, page, serializer):
    """
    Worker function for one page.
    Each thread gets its own DB connection lifecycle.
    """
    thread_id = threading.get_ident()
    try:
        close_old_connections()
        manager = manager_cls(page, serializer)
        manager.batch_fetch_validate_store_resource_data()
        print(f"Thread Id: {thread_id}, [{manager_cls.__name__}] finished page {page}")
    except Exception as e:
        print(
            f"Thread Id: {thread_id}, [{manager_cls.__name__}] error on page {page}: {e}"
        )
        raise
    finally:
        close_old_connections()


def ingest_resource(manager_cls, serializer):
    """
    Ingest all pages for a given SWAPI resource type.

    Executes the ingestion pipeline in parallel across multiple worker
    threads. Each worker fetches, validates, and stores a single page of
    data using the provided manager class.

    Args:
        manager_cls (type[SWAPIResourceManager]): Manager class handling
            ingestion for a specific resource type (e.g., films, characters).
        serializer (Serializer): DRF serializer for validating resource data.

    Returns:
        float: Total elapsed time for ingestion in seconds.

    Notes:
        - The number of workers is capped using `determine_max_worker_units()`.
        - Uses `ThreadPoolExecutor` for parallel page ingestion.
        - Each worker manages its own database connection lifecycle.
    """
    start_time = time.time()

    total_pages = manager_cls.pages_count()
    max_workers = determine_max_worker_units()
    print(
        f"[{manager_cls.__name__}] ingesting {total_pages} pages with {max_workers} workers"
    )
    runner_partial = functools.partial(
        run_manager_for_page, manager_cls, serializer=serializer
    )
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        list(executor.map(runner_partial, range(1, total_pages + 1)))

    return time.time() - start_time


def threaded_through_tables_population():
    """
    Populate all many-to-many through tables in parallel.

    Spawns one worker per resource type manager (Films, Characters,
    Starships). Each worker resolves staged relationships into the
    corresponding through table using bulk SQL inserts.

    Returns:
        float: Total elapsed time for through table population in seconds.

    Notes:
        - The number of workers is fixed to 3 (one per manager).
        - Uses raw SQL inserts for performance.
        - Skips duplicates via `ON CONFLICT DO NOTHING`.
    """
    start_time = time.time()
    swapi_managers = [
        SWAPIFilmsManager,
        SWAPICharactersManager,
        SWAPIStarshipsManager,
    ]
    with ThreadPoolExecutor(max_workers=3) as executor:
        list(executor.map(lambda mng: mng.batch_through_table_insert(), swapi_managers))
    return time.time() - start_time


def fetch_populate_exception_handler(func):
    """
    Decorator handling potential exceptions from:
    - Fetching SWAPI data
    - Database population
    Keeps handling in a single dedicated place.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RequestException as e:
            status_code = getattr(
                e.response, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            response_data = {"error": "API request failed", "details": str(e)}
            return Response(response_data, status=status_code)
        except ValidationError as e:
            response_data = {"error": "Validation failed", "details": e.detail}
            return Response(response_data, status=e.status_code)
        except DBError as e:
            response_data = {"error": "Database operation failed", "details": str(e)}
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            response_data = {"error": "Internal server error", "details": str(e)}
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return wrapper
