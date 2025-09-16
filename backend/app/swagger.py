from drf_spectacular.utils import OpenApiParameter

PAGE_QUERY_PARAM = OpenApiParameter(
    name="page",
    type=int,
    description="The page number of the paginated results to retrieve.",
)

TITLE_CONTAINS_QUERY_PARAM = OpenApiParameter(
    name="contains",
    type=str,
    required=False,
    description='Filter by substring contained in "title".',
)

NAME_CONTAINS_QUERY_PARAM = OpenApiParameter(
    name="contains",
    type=str,
    required=False,
    description='Filter by substring contained in "name".',
)

FILMS_QUERY_PARAMS = [PAGE_QUERY_PARAM, TITLE_CONTAINS_QUERY_PARAM]

CHARACTERS_QUERY_PARAMS = STARSHIPS_QUERY_PARAMS = [
    PAGE_QUERY_PARAM,
    NAME_CONTAINS_QUERY_PARAM,
]

FETCH_POPULATE_QUERY_PARAMS = [
    OpenApiParameter(
        name="threads",
        type=bool,
        required=False,
        description="With `True`, fetches the SWAPI data in a separate thread per resource to optimize performance",
    ),
]
