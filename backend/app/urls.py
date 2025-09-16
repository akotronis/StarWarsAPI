from django.urls import include, path
from rest_framework import routers

from . import views

app_name = "app"

router = routers.DefaultRouter(trailing_slash=False)
router.register("films", views.FilmViewSet, basename="films")
router.register("characters", views.CharacterViewSet, basename="characters")
router.register("starships", views.StarshipViewSet, basename="starships")
router.register(
    "swapi-fetch-populate",
    views.SWAPIFetchPopulateView,
    basename="swapi-fetch-populate",
)

urlpatterns = [
    path("", include(router.urls)),
]
