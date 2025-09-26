def id_from_swapi_detail_url(url):
    """
    From a swapi detail url extract last item from path.
    Args:
        url (str): A swapi detail url
    
    Returns:
        int: The resource id as int
    """
    return int(url.split('/')[-1])