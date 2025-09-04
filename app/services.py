import functools

from django.db import Error as DBError, transaction
from requests.exceptions import RequestException
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from . import clients
from . import models


def fetch_and_validate_data(url, serializer):
    fetched_data = clients.get_swapi_data(url)
    serializer_instance = serializer(data=fetched_data, many=True)
    try:
        serializer_instance.is_valid(raise_exception=True)
    except ValidationError as e:
        error_message = str(e)
        if hasattr(e, 'detail'):
            error_message = [{'url': url, 'data': fetched_data[i], 'error': v} for i,v in enumerate(e.detail) if v]
        raise ValidationError(error_message)
    return serializer_instance.validated_data


def create_films(films_data):
    films_to_create = []
    film_mappings = {}
    fields = ['title', 'episode_id', 'director', 'release_date', 'created']
    
    for film_data in films_data:
        film = models.Film(**{field: film_data[field] for field in fields})
        films_to_create.append(film)
        film_mappings[film_data['url']] = film
    
    models.Film.objects.bulk_create(films_to_create)
    return film_mappings


def create_characters(characters_data):
    characters_to_create = []
    character_mappings = {}
    fields = ['name', 'height', 'gender', 'created']
    
    for character_data in characters_data:
        character = models.Character(**{field: character_data[field] for field in fields})
        characters_to_create.append(character)
        character_mappings[character_data['url']] = character
    
    models.Character.objects.bulk_create(characters_to_create)
    return character_mappings


def create_starships(starships_data):
    starships_to_create = []
    starship_mappings = {}
    fields = ['name', 'model', 'cost_in_credits', 'hyperdrive_rating', 'created']
    
    for starship_data in starships_data:
        starship = models.Character(**{field: starship_data[field] for field in fields})
        starships_to_create.append(starship)
        starship_mappings[starship_data['url']] = starship
    
    models.Starship.objects.bulk_create(starships_to_create)
    return starship_mappings


def create_character_film_relationships(characters_data, character_mappings, film_mappings):
    character_film_table = models.Character.films.through
    character_film_objects = []
    
    for character_data in characters_data:
        character = character_mappings.get(character_data['url'])
        for film_url in character_data['films']:
            if (film := film_mappings.get(film_url)):
                character_film_obj = character_film_table(character_id=character.pk, film_id=film.pk)
                character_film_objects.append(character_film_obj)
    
    if character_film_objects:
        character_film_table.objects.bulk_create(character_film_objects)


def create_film_starship_relationships(films_data, film_mappings, starship_mappings):
    film_starship_table = models.Film.starships.through
    film_starship_objects = []
    
    for film_data in films_data:
        film = film_mappings.get(film_data['url'])
        for starship_url in film_data['starships']:
            starship = starship_mappings.get(starship_url)
            if (starship := starship_mappings.get(starship_url)):
                film_starship_obj = film_starship_table(film_id=film.id, starship_id=starship.id)
                film_starship_objects.append(film_starship_obj)
    
    if film_starship_objects:
        film_starship_table.objects.bulk_create(film_starship_objects)


def update_starship_characters(characters_data, character_mappings, starship_mappings):
    starship_updates = []
    
    for character_data in characters_data:
        character = character_mappings.get(character_data['url'])
        for starship_url in character_data['starships']:
            if (starship := starship_mappings.get(starship_url)):
                starship.character = character
                starship_updates.append(starship)
    
    if starship_updates:
        models.Starship.objects.bulk_update(starship_updates, ['character'])


def clear_tables():
    for model in [models.Film, models.Character, models.Starship]:
        model.objects.all().delete()


@transaction.atomic
def populate_database(films_data, characters_data, starships_data):
    # Start fresh
    clear_tables()
    
    film_mappings = create_films(films_data)
    character_mappings = create_characters(characters_data)
    starship_mappings = create_starships(starships_data)
    create_character_film_relationships(characters_data, character_mappings, film_mappings)
    create_film_starship_relationships(films_data, film_mappings, starship_mappings)
    update_starship_characters(characters_data, character_mappings, starship_mappings)


def exception_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RequestException as e:
            status_code = getattr(e.response, 'status_code', status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({'error': 'API request failed', 'details': str(e)}, status=status_code)
        except ValidationError as e:
            return Response({'error': 'Validation failed', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except DBError as e:
            return Response({'error': 'Database operation failed', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': 'Internal server error', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return wrapper

    