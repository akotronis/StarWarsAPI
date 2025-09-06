from django.test import TestCase

from .. import models


class FilmModelTest(TestCase):
    def test_create_film(self):
        """Test Film model creation and string representation"""
        film = models.Film.objects.create(
            title="A New Hope",
            episode_id=4,
            director="George Lucas",
            release_date="1977-05-25",
        )
        self.assertEqual(film.title, "A New Hope")
        self.assertEqual(film.episode_id, 4)
        self.assertEqual(
            str(film),
            "(1) Title: A New Hope, Director: George Lucas, Release date: 1977-05-25",
        )

    def test_film_optional_fields(self):
        """Test Film with optional fields as None/empty strings"""
        film = models.Film.objects.create(title="Test Film")
        self.assertIsNone(film.episode_id)
        self.assertEqual(film.director, "")
        self.assertIsNone(film.release_date)
        self.assertIsNone(film.swapi_url)


class CharacterModelTest(TestCase):
    def test_create_character(self):
        """Test Character model creation"""
        character = models.Character.objects.create(
            name="Luke Skywalker", height=172.5, gender="male"
        )
        self.assertEqual(character.name, "Luke Skywalker")
        self.assertEqual(character.height, 172.5)
        self.assertEqual(
            str(character), "(1) Name: Luke Skywalker, Gender: male, Height: 172.5"
        )

    def test_character_null_height(self):
        """Test Character with null height"""
        character = models.Character.objects.create(name="R2-D2", gender="n/a")
        self.assertIsNone(character.height)


class StarshipModelTest(TestCase):
    def test_create_starship(self):
        """Test Starship model creation"""
        starship = models.Starship.objects.create(
            name="Millennium Falcon",
            model="YT-1300 light freighter",
            cost_in_credits=100000,
            hyperdrive_rating=0.5,
        )
        self.assertEqual(starship.name, "Millennium Falcon")
        self.assertEqual(starship.cost_in_credits, 100000)
        self.assertEqual(
            str(starship), "(1) Name: Millennium Falcon, Model: YT-1300 light freighter"
        )

    def test_starship_with_null_values(self):
        """Test Starship with null cost and hyperdrive"""
        starship = models.Starship.objects.create(name="X-Wing", model="T-65")
        self.assertIsNone(starship.cost_in_credits)
        self.assertIsNone(starship.hyperdrive_rating)
