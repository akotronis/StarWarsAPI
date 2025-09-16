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


@extend_schema(
    description='Fetch resources **"films, characters, starships"** from SWAPI and populate database',
    tags=["Action: Fetch and populate local database"],
)
@extend_schema_view(list=extend_schema(parameters=swagger.FETCH_POPULATE_QUERY_PARAMS))
class SWAPIFetchPopulateView(viewsets.ViewSet):
    """
    Fetch resources "films, characters, starships" from SWAPI and populate database.
    Use "threads=true" to fetch SWAPI data in a separate thread per resource for optimized performance.
    """

    swapi_urls = [
        constants.SWAPI_FILMS_URL,
        constants.SWAPI_CHARACTERS_URL,
        constants.SWAPI_STARSHIPS_URL,
    ]
    swapi_serializers = [
        serializers.SWAPIFilmSerializer,
        serializers.SWAPICharacterSerializer,
        serializers.SWAPIStarshipSerializer,
    ]

    @services.fetch_populate_exception_handler
    def list(self, request):
        # Fetch SWAPI data
        fetch_start_time = time.time()
        qparams = swapi.utils.validate_from_request(
            serializers.ThreadsQueryParamSerializer, self.request, attr="query_params"
        )
        if threads := qparams.get("threads"):
            fetched_data = services.fetch_and_validate_all_data_in_threads(
                self.swapi_urls, self.swapi_serializers
            )
        else:
            fetched_data = [
                services.fetch_and_validate_data(url, srlz)
                for url, srlz in zip(self.swapi_urls, self.swapi_serializers)
            ]
        fetch_elapsed = time.time() - fetch_start_time

        # Populate database
        populate_start_time = time.time()
        services.populate_database(*fetched_data)
        populate_elapsed = time.time() - populate_start_time

        report = services.make_fetch_populate_report(
            *fetched_data, fetch_elapsed, populate_elapsed, threads
        )
        return Response(report)
