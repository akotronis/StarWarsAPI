from drf_spectacular.utils import OpenApiParameter


SWAGGER_QUERY_PARAMS = [
        OpenApiParameter(
        name='contains',
        type=str,
        required=False,
        description='Filter by substring contained in "name"/"title".'
    ),
        OpenApiParameter(
        name='page',
        type=int,
        description='The page number of the paginated results to retrieve.'
    ),
]
