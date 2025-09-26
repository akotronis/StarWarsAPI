import time

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.response import Response

import swapi.utils

from . import constants, mixins, models, serializers, services, swagger


@extend_schema(
    description="Get **Film** resources from local database", tags=["Resource: Films"]
)
@extend_schema_view(list=extend_schema(parameters=swagger.FILMS_QUERY_PARAMS))
class FilmViewSet(mixins.CommonFunctionalityViewsetMixin, viewsets.ModelViewSet):
    """
    View for Film resource.
    Filter by:
    - "title" with "contains=<string>"
    - page number with "page=<number>"
    """

    serializer_class = serializers.FilmSerializer
    queryset = models.Film.objects.all().prefetch_related(
        constants.ResourceEnum.STARSHIP.plural, constants.ResourceEnum.CHARACTER.plural
    )
    filter_field = "title"


@extend_schema(
    description="Get **Character** resources from local database",
    tags=["Resource: Characters"],
)
@extend_schema_view(list=extend_schema(parameters=swagger.CHARACTERS_QUERY_PARAMS))
class CharacterViewSet(mixins.CommonFunctionalityViewsetMixin, viewsets.ModelViewSet):
    """
    View for Character resource.
    Filter by:
    - "name" with "contains=<string>"
    - page number with "page=<number>"
    """

    serializer_class = serializers.CharacterSerializer
    queryset = models.Character.objects.all().prefetch_related(
        constants.ResourceEnum.FILM.plural, constants.ResourceEnum.STARSHIP.plural
    )


@extend_schema(
    description="Get **Starship** resources from local database",
    tags=["Resource: Starships"],
)
@extend_schema_view(list=extend_schema(parameters=swagger.STARSHIPS_QUERY_PARAMS))
class StarshipViewSet(mixins.CommonFunctionalityViewsetMixin, viewsets.ModelViewSet):
    """
    View for Starship resource.
    Filter by:
    - "name" with "contains=<string>"
    - page number with "page=<number>"
    """

    serializer_class = serializers.StarshipSerializer
    queryset = models.Starship.objects.all().prefetch_related(
        constants.ResourceEnum.FILM.plural, constants.ResourceEnum.CHARACTER.plural
    )


@extend_schema(
    description='Fetch resources **"films, characters, starships"** from SWAPI and populate database',
    tags=["Action: Fetch and populate local database"],
)
class SWAPIFetchPopulateView(viewsets.ViewSet):
    """
    Fetch resources "films, characters, starships" from SWAPI and populate database.
    Fetching/validation/database population is performed in threads for scaling.
    """

    swapi_managers = [
        services.SWAPIFilmsManager,
        services.SWAPICharactersManager,
        services.SWAPIStarshipsManager,
    ]
    swapi_serializers = [
        serializers.SWAPIFilmSerializer,
        serializers.SWAPICharacterSerializer,
        serializers.SWAPIStarshipSerializer,
    ]
    swapi_counts = [
        constants.TOTAL_FILMS,
        constants.TOTAL_CHARACTERS,
        constants.TOTAL_STARSHIPS,
    ]

    # @services.fetch_populate_exception_handler
    def list(self, request):
        services.clear_tables()
        durations = [
            services.ingest_resource(mng, srlz)
            for mng, srlz in zip(self.swapi_managers, self.swapi_serializers)
        ]
        names = map(lambda x: x.entity_model.__name__, self.swapi_managers)
        counts = list(
            map(lambda x: x.entity_model.objects.count(), self.swapi_managers)
        )
        resources_report = {
            f"{name}s": {
                "Count": info[0],
                "Duration": swapi.utils.format_elapsed_time(info[1]),
            }
            for name, info in zip(names, zip(counts, durations))
        }

        through_tables_duration = services.threaded_through_tables_population()
        through_tables_report = {
            "Through Tables Duration": swapi.utils.format_elapsed_time(
                through_tables_duration
            )
        }
        total_report = {
            "Total": {
                "Count": sum(counts),
                "Duration": swapi.utils.format_elapsed_time(sum(durations)),
            }
        }
        return Response(resources_report | through_tables_report | total_report)
