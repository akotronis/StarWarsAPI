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


INSERT_CHUNK_TO_THROUGH_TABLE_SQL_TEMPLATE = """
    WITH batch as (
        SELECT sr.id, from_.id AS from_id, to_.id AS to_id
        FROM {} sr
        JOIN {} from_ ON sr.from_swapi_id = from_.swapi_id
        JOIN {} to_ ON sr.to_swapi_id = to_.swapi_id
        WHERE sr.from_type = '{}'
            AND sr.to_type = '{}'
            AND sr.id > {}
        ORDER BY sr.id
        LIMIT {}
    )
    INSERT INTO {} ({})
    SELECT from_id, to_id FROM batch;
"""

FILTERED_STAGED_RELATIONSHIPS_TABLE_MAX_ID_SQL_TEMPLATE = """
    SELECT MAX(id) FROM {}
    WHERE from_type = '{}'
        AND to_type = '{}'
        AND id > {}
"""

TOTAL_FILMS = 1_000
TOTAL_CHARACTERS = 5_000
TOTAL_STARSHIPS = 2_000
PAGE_SIZE = 1_000
CHUNK_SIZE = 1_000
WORKER_THRESHOLD = 10
