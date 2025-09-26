from django.db import models

class ResourceEnum(models.TextChoices):
    FILM = "film"
    CHARACTER = "character"
    STARSHIP = "starship"

    @property
    def plural(self):
        return f"{self.value}s"
    

# SWAPI_BASE_URL = "https://swapi.info/api"
SWAPI_BASE_URL = "http://srv-sw-mock:8080"
SWAPI_FILMS_URL = f"{SWAPI_BASE_URL}/films"
SWAPI_CHARACTERS_URL = f"{SWAPI_BASE_URL}/people"
SWAPI_STARSHIPS_URL = f"{SWAPI_BASE_URL}/starships"

TOTAL_FILMS = 1_000_000
TOTAL_CHARACTERS = 5_000_000
TOTAL_STARSHIPS = 2_000_000
PAGE_SIZE = 1000
