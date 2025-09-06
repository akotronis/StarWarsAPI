import functools

from django.db import Error as DBError, transaction
from requests.exceptions import RequestException
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from . import clients
from . import models


def fetch_and_validate_data(url, serializer):
    """
    Fetch, validate and return data from SWAPI

    Args:
        url (str): SWAPI resource url
        serializer (Serializer): Django REST Framework serializer class
            used to validate and transform the API response data

    Raises:
        ValidationError: Catch and reraise for more descriptive message
            Include thew SWAPI resource thta caused the error along with
            the error.

    Returns:
        list[dict]: Validated data
    """
    fetched_data = clients.get_swapi_data(url)
    serializer_instance = serializer(data=fetched_data, many=True)
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


def create_films(films_data):
    """
    Create Film objects in bulk from validated SWAPI data and return URL mappings.

    Processes a list of film data dictionaries, creates Film model instances,
    performs bulk database insertion, and returns a mapping of SWAPI URLs to
    the created Film instances for relationship establishment. Uses safe field
    access with .get() to handle missing data gracefully.

    Args:
        films_data (list[dict]): List of validated film data dictionaries from SWAPI.
            Each dictionary should contain keys: 'title', 'episode_id', 'director',
            'release_date', 'created', and 'swapi_url'. Missing optional fields will
            be set to None.

    Returns:
        dict[str, Film]: Mapping of SWAPI URLs to created Film instances. The keys are SWAPI URLs
        (str) and the values are the corresponding Film model instances. This mapping
        is essential for establishing relationships with other entities (characters,
        starships) that reference films by URL.

    Notes:
        - Uses bulk_create for optimal database performance
        - Uses .get() for safe field access (missing fields become None)
        - The 'swapi_url' field is required for the mapping functionality
        - Expects validated data but handles missing optional fields gracefully
        - The returned mapping is crucial for establishing many-to-many relationships
    """
    films_to_create = []
    film_mappings = {}
    fields = ["title", "episode_id", "director", "release_date", "created", "swapi_url"]

    for film_data in films_data:
        film = models.Film(**{field: film_data.get(field) for field in fields})
        films_to_create.append(film)
        film_mappings[film_data["swapi_url"]] = film

    models.Film.objects.bulk_create(films_to_create)
    return film_mappings


def create_characters(characters_data):
    """
    Create Character objects in bulk from validated SWAPI data and return URL mappings.

    Processes a list of character data dictionaries, creates Character model instances,
    performs bulk database insertion, and returns a mapping of SWAPI URLs to
    the created Character instances for relationship establishment. Uses safe field
    access with .get() to handle missing data gracefully.

    Args:
        characters_data (list[dict]): List of validated character data dictionaries from SWAPI.
            Each dictionary should contain keys: 'name', 'height', 'gender', 'created',
            and 'swapi_url'. Missing optional fields will be set to None.

    Returns:
        dict[str, Character]: Mapping of SWAPI URLs to created Character instances. The keys are SWAPI URLs
        (str) and the values are the corresponding Character model instances. This mapping
        is essential for establishing relationships with other entities (films, starships)
        that reference characters by URL.

    Notes:
        - Uses bulk_create for optimal database performance
        - Uses .get() for safe field access (missing fields become None)
        - The 'swapi_url' field is required for the mapping functionality
        - Expects validated data but handles missing optional fields gracefully
        - The returned mapping is crucial for establishing many-to-many relationships
    """
    characters_to_create = []
    character_mappings = {}
    fields = ["name", "height", "gender", "created", "swapi_url"]

    for character_data in characters_data:
        character = models.Character(
            **{field: character_data.get(field) for field in fields}
        )
        characters_to_create.append(character)
        character_mappings[character_data["swapi_url"]] = character

    models.Character.objects.bulk_create(characters_to_create)
    return character_mappings


def create_starships(starships_data):
    """
    Create Starship objects in bulk from validated SWAPI data and return URL mappings.

    Processes a list of starship data dictionaries, creates Starship model instances,
    performs bulk database insertion, and returns a mapping of SWAPI URLs to
    the created Starship instances for relationship establishment. Uses safe field
    access with .get() to handle missing data gracefully.

    Args:
        starships_data (list[dict]): List of validated starship data dictionaries from SWAPI.
            Each dictionary should contain keys: 'name', 'model', 'cost_in_credits',
            'hyperdrive_rating', 'created', and 'swapi_url'. Missing optional fields will
            be set to None.

    Returns:
        dict: Mapping of SWAPI URLs to created Starship instances. The keys are SWAPI URLs
        (str) and the values are the corresponding Starship model instances. This mapping
        is essential for establishing relationships with other entities (films, characters)
        that reference starships by URL.

    Notes:
        - Uses bulk_create for optimal database performance
        - Uses .get() for safe field access (missing fields become None)
        - The 'swapi_url' field is required for the mapping functionality
        - Expects validated data but handles missing optional fields gracefully
        - The returned mapping is crucial for establishing many-to-many relationships
    """
    starships_to_create = []
    starship_mappings = {}
    fields = [
        "name",
        "model",
        "cost_in_credits",
        "hyperdrive_rating",
        "created",
        "swapi_url",
    ]
    for starship_data in starships_data:
        starship = models.Starship(
            **{field: starship_data.get(field) for field in fields}
        )
        starships_to_create.append(starship)
        starship_mappings[starship_data["swapi_url"]] = starship

    models.Starship.objects.bulk_create(starships_to_create)
    return starship_mappings


def create_film_starship_relationships(films_data, film_mappings, starship_mappings):
    """
    Create many-to-many relationships between Films and Starships in bulk.

    Processes film data to establish relationships between films and their associated
    starships using URL mappings. Creates through model objects for bulk insertion.

    Args:
        films_data (list[dict]): List of film data dictionaries from SWAPI, each
            containing a 'starships' list with starship URLs.
        film_mappings (dict): Mapping of SWAPI URLs to Film model instances.
        starship_mappings (dict): Mapping of SWAPI URLs to Starship model instances.

    Notes:
        - Only creates relationships if both film and starship exist in mappings
        - Uses bulk_create for optimal performance
        - Handles missing mappings gracefully (skips non-existent relationships)
    """
    film_starship_table = models.Film.starships.through
    film_starship_objects = []

    for film_data in films_data:
        film = film_mappings.get(film_data["swapi_url"])
        for starship_url in film_data.get("starships", []):
            starship = starship_mappings.get(starship_url)
            if starship := starship_mappings.get(starship_url):
                film_starship_obj = film_starship_table(
                    film_id=film.id, starship_id=starship.id
                )
                film_starship_objects.append(film_starship_obj)

    if film_starship_objects:
        film_starship_table.objects.bulk_create(film_starship_objects)


def create_character_film_relationships(
    characters_data, character_mappings, film_mappings
):
    """
    Create many-to-many relationships between Characters and Films in bulk.

    Processes character data to establish relationships between characters and their
    associated films using URL mappings. Creates through model objects for bulk insertion.

    Args:
        characters_data (list[dict]): List of character data dictionaries from SWAPI,
            each containing a 'films' list with film URLs.
        character_mappings (dict): Mapping of SWAPI URLs to Character model instances.
        film_mappings (dict): Mapping of SWAPI URLs to Film model instances.

    Notes:
        - Only creates relationships if both character and film exist in mappings
        - Uses bulk_create for optimal performance
        - Handles missing mappings gracefully (skips non-existent relationships)
    """
    character_film_table = models.Character.films.through
    character_film_objects = []

    for character_data in characters_data:
        character = character_mappings.get(character_data["swapi_url"])
        for film_url in character_data.get("films", []):
            if film := film_mappings.get(film_url):
                character_film_obj = character_film_table(
                    character_id=character.pk, film_id=film.pk
                )
                character_film_objects.append(character_film_obj)

    if character_film_objects:
        character_film_table.objects.bulk_create(character_film_objects)


def create_starship_character_relationships(
    starships_data, starship_mappings, character_mappings
):
    """
    Create many-to-many relationships between Starships and Characters in bulk.

    Processes starship data to establish relationships between starships and their
    associated characters (pilots) using URL mappings. Creates through model objects
    for bulk insertion.

    Args:
        starships_data (list[dict]): List of starship data dictionaries from SWAPI,
            each containing a 'characters' list with character URLs.
        starship_mappings (dict): Mapping of SWAPI URLs to Starship model instances.
        character_mappings (dict): Mapping of SWAPI URLs to Character model instances.

    Notes:
        - Only creates relationships if both starship and character exist in mappings
        - Uses bulk_create for optimal performance
        - Handles missing mappings gracefully (skips non-existent relationships)
        - Note: In SWAPI, 'characters' field represents pilots of the starship
    """
    starship_character_table = models.Starship.characters.through
    starship_character_objects = []

    for starship_data in starships_data:
        starship = starship_mappings.get(starship_data["swapi_url"])
        for character_url in starship_data.get("characters", []):
            character = character_mappings.get(character_url)
            if character := character_mappings.get(character_url):
                starship_character_obj = starship_character_table(
                    starship_id=starship.id, character_id=character.id
                )
                starship_character_objects.append(starship_character_obj)

    if starship_character_objects:
        starship_character_table.objects.bulk_create(starship_character_objects)


def clear_tables():
    """
    Function to clean tables for starting fresh
    """
    for model in [models.Film, models.Character, models.Starship]:
        model.objects.all().delete()


@transaction.atomic
def populate_database(films_data, characters_data, starships_data):
    """
    Function implementing logic for database population in transaction.
    Rollback all database operaations if any error occurs.
    Clears tables first for fresh initialization.

    Args:
        films_data (dict): Validated films SWAPI data
        characters_data (dict): Validated characters SWAPI data
        starships_data (dict): Validated starships SWAPI data
    """
    clear_tables()

    film_mappings = create_films(films_data)
    character_mappings = create_characters(characters_data)
    starship_mappings = create_starships(starships_data)
    create_film_starship_relationships(films_data, film_mappings, starship_mappings)
    create_character_film_relationships(
        characters_data, character_mappings, film_mappings
    )
    create_starship_character_relationships(
        starships_data, starship_mappings, character_mappings
    )


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
