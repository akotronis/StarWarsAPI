from math import ceil
from typing import Generic, List, Optional, TypeVar
from urllib.parse import urljoin

from fastapi import FastAPI, Query
from pydantic import BaseModel
from pydantic.generics import GenericModel

HOST_URL = "http://srv-sw-mock:8080"
SWAPI_BASE_URL = "https://swapi.info/api"

app = FastAPI(title="Mock SWAPI Server")

# ----------------------------
# Configuration
# ----------------------------
TOTAL_FILMS = 1_000
TOTAL_CHARACTERS = 5_000
TOTAL_STARSHIPS = 2_000
PAGE_SIZE = 1_000


# ----------------------------
# Pydantic models
# ----------------------------
class Film(BaseModel):
    title: str
    episode_id: int
    director: str
    release_date: str
    url: str
    starships: List[str]


class Character(BaseModel):
    name: str
    height: float
    gender: str
    url: str
    films: List[str]


class Starship(BaseModel):
    name: str
    model: str
    cost_in_credits: int
    hyperdrive_rating: float
    url: str
    pilots: List[str]


T = TypeVar("T", Film, Character, Starship)


class PaginatedResponse(GenericModel, Generic[T]):
    count: int
    next: Optional[str]
    previous: Optional[str]
    results: List[T]


# ----------------------------
# Helpers
# ----------------------------
def _build_page_url(host: str, resource: str, page: int) -> str:
    # normalize slashes
    host = host.rstrip("/")
    resource = resource.lstrip("/")
    return f"{host}/{resource}?page={page}"


def paginate_factory(
    total: int,
    page: int,
    resource_name: str,
    builder: callable,
    host_url: str = HOST_URL,
) -> PaginatedResponse:
    if page < 1:
        page = 1

    total_pages = ceil(total / PAGE_SIZE)
    start = (page - 1) * PAGE_SIZE
    end = min(start + PAGE_SIZE, total)

    results = [builder(i) for i in range(start, end)]

    next_url = (
        _build_page_url(host_url, resource_name, page + 1)
        if page < total_pages
        else None
    )
    previous_url = (
        _build_page_url(host_url, resource_name, page - 1) if page > 1 else None
    )

    return PaginatedResponse(
        count=total, next=next_url, previous=previous_url, results=results
    )


# ----------------------------
# Endpoints
# ----------------------------
@app.get("/films", response_model=PaginatedResponse[Film])
def get_films(page: int = Query(1, ge=1)):
    def film_builder(i: int) -> Film:
        return Film(
            title=f"Film {i}",
            episode_id=i,
            director=f"Director {i % 10}",
            release_date=f"2025-01-{(i % 28) + 1:02d}",
            url=f"{SWAPI_BASE_URL}/films/{i}",
            starships=[f"{SWAPI_BASE_URL}/starships/{j}" for j in range(i * 2, i * 2 + 3) if j < TOTAL_STARSHIPS],
        )

    return paginate_factory(TOTAL_FILMS, page, "films", film_builder)


@app.get("/people", response_model=PaginatedResponse[Character])
def get_characters(page: int = Query(1, ge=1)):
    def character_builder(i: int) -> Character:
        return Character(
            name=f"Character {i}",
            height=150 + (i % 50),
            gender="male" if i % 2 == 0 else "female",
            url=f"{SWAPI_BASE_URL}/people/{i}",
            films=[
                f"{SWAPI_BASE_URL}/films/{j % TOTAL_FILMS}" for j in range(i % TOTAL_FILMS, (i % TOTAL_FILMS) + 2)
            ],
        )

    return paginate_factory(TOTAL_CHARACTERS, page, "people", character_builder)


@app.get("/starships", response_model=PaginatedResponse[Starship])
def get_starships(page: int = Query(1, ge=1)):
    def starship_builder(i: int) -> Starship:
        return Starship(
            name=f"Starship {i}",
            model=f"Model {i % 50}",
            cost_in_credits=1000000 + i * 1000,
            hyperdrive_rating=round(0.5 + (i % 10) * 0.1, 1),
            url=f"{SWAPI_BASE_URL}/starships/{i}",
            pilots=[
                f"{SWAPI_BASE_URL}/films/{j % TOTAL_CHARACTERS}"
                for j in range(i % TOTAL_CHARACTERS, (i % TOTAL_CHARACTERS) + 2)
            ],
        )

    return paginate_factory(TOTAL_STARSHIPS, page, "starships", starship_builder)
