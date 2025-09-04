from rest_framework import viewsets
from rest_framework.response import Response

from . import constants
from . import mixins
from . import models
from . import serializers
from . import services


class FilmViewSet(mixins.CommonFunctionalityViewsetMixin, viewsets.ModelViewSet):
    """
    View for Film resource.
    Filter by:
    - "title" with "contains=<string>"
    - page number with "page=<number>"
    """
    serializer_class = serializers.FilmSerializer
    queryset = models.Film.objects.all()
    filter_field = 'title'


class CharacterViewSet(mixins.CommonFunctionalityViewsetMixin, viewsets.ModelViewSet):
    """
    View for Character resource.
    Filter by:
    - "name" with "contains=<string>"
    - page number with "page=<number>"
    """
    serializer_class = serializers.CharacterSerializer
    queryset = models.Character.objects.all()


class StarshipViewSet(mixins.CommonFunctionalityViewsetMixin, viewsets.ModelViewSet):
    """
    View for Starship resource.
    Filter by:
    - "name" with "contains=<string>"
    - page number with "page=<number>"
    """
    serializer_class = serializers.StarshipSerializer
    queryset = models.Starship.objects.all()


# By using ViewSet, this can be registered via router and appear in the DRF Browser API root view
class SWAPIFetchPopulateView(viewsets.ViewSet):
    """
    Fetch resources "films, characters, starships" from SWAPI and populate database
    """
    @services.exception_handler
    def list(self, request):
        films_data = services.fetch_and_validate_data(constants.SWAPI_FILMS_URL, serializers.SWAPIFilmSerializer)
        characters_data = services.fetch_and_validate_data(constants.SWAPI_CHARACTERS_URL, serializers.SWAPICharacterSerializer)
        starships_data = services.fetch_and_validate_data(constants.SWAPI_STARSHIPS_URL, serializers.SWAPIStarshipSerializer)
        services.populate_database(films_data, characters_data, starships_data)
        return Response({'test': 1})
