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
    queryset = models.Film.objects.all().prefetch_related("starships", "characters")
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
    queryset = models.Character.objects.all().prefetch_related("films", "starships")


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
    queryset = models.Starship.objects.all().prefetch_related("films", "characters")


@extend_schema(description=" ", tags=["Action: Fetch and populate local database"])
class SWAPIFetchPopulateView(viewsets.ViewSet):
    """
    Fetch resources "films, characters, starships" from SWAPI and populate database
    """

    @services.fetch_populate_exception_handler
    def list(self, request):
        # Fetch SWAPI data
        fetch_start_time = time.time()
        films_data = services.fetch_and_validate_data(
            constants.SWAPI_FILMS_URL, serializers.SWAPIFilmSerializer
        )
        characters_data = services.fetch_and_validate_data(
            constants.SWAPI_CHARACTERS_URL, serializers.SWAPICharacterSerializer
        )
        starships_data = services.fetch_and_validate_data(
            constants.SWAPI_STARSHIPS_URL, serializers.SWAPIStarshipSerializer
        )
        fetch_elapsed = time.time() - fetch_start_time

        # Populate database
        populate_start_time = time.time()
        services.populate_database(films_data, characters_data, starships_data)
        populate_elapsed = time.time() - populate_start_time

        resource_names = ["Films", "Characters", "Starships"]
        managers = [
            models.Film.objects,
            models.Character.objects,
            models.Starship.objects,
        ]
        model_counts = dict(zip(resource_names, map(lambda obj: obj.count(), managers)))
        fetched_data = [films_data, characters_data, starships_data]
        api_counts = dict(zip(resource_names, map(len, fetched_data)))
        report = {
            "Fetched SWAPI data successfully": {
                "time": swapi.utils.format_elapsed_time(fetch_elapsed),
                "counts": model_counts,
            },
            "Populated database successfully": {
                "time": swapi.utils.format_elapsed_time(populate_elapsed),
                "counts": api_counts,
            },
        }
        return Response(report)
