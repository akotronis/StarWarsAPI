import requests


def get_swapi_data(url):
    """
    Function fetching data from paginated SWAPI response

    Args:
        url (str): The SWAPI url to fetch data from

    Returns:
        list[dict]: list of dict resource data
    """
    response = requests.get(url)
    response.raise_for_status()
    return response.json().get('results')
