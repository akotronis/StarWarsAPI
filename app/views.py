from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from . import mixins
from . import models
from . import serializers


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
    def list(self, request):
        return Response({'test': 1})
