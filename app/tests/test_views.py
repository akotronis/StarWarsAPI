from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .. import models


class FilmViewSetTest(APITestCase):
    def setUp(self):
        # Create test data in database
        self.film1 = models.Film.objects.create(
            title="A New Hope",
            episode_id=4,
            director="George Lucas",
            release_date="1977-05-25",
        )
        self.film2 = models.Film.objects.create(
            title="The Empire Strikes Back",
            episode_id=5,
            director="Irvin Kershner",
            release_date="1980-05-21",
        )

    def test_get_films_success(self):
        """Test successful films endpoint with database data"""
        url = reverse("app:films-list")
        response = self.client.get(url)
        data = response.data["results"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["title"], "A New Hope")
        self.assertEqual(data[1]["episode_id"], 5)

    def test_get_films_filtered(self):
        """Test films endpoint with title filter"""
        url = reverse("app:films-list") + "?contains=Hope"
        response = self.client.get(url)
        data = response.data["results"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["title"], "A New Hope")

    def test_get_films_empty_filter(self):
        """Test films endpoint with filter that returns no results"""
        url = reverse("app:films-list") + "?contains=nonexistent"
        response = self.client.get(url)
        data = response.data["results"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 0)

    def test_get_film_detail(self):
        """Test film detail endpoint"""
        url = reverse("app:films-detail", kwargs={"pk": self.film1.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "A New Hope")


class CharacterViewSetTest(APITestCase):
    def setUp(self):
        self.character1 = models.Character.objects.create(
            name="Luke Skywalker",
            height=172,
            gender="male",
            swapi_url="https://swapi.info/api/people/2/",
        )
        self.character2 = models.Character.objects.create(
            name="Darth Vader",
            height=202,
            gender="male",
            swapi_url="https://swapi.info/api/people/2/",
        )

    def test_get_characters_success(self):
        """Test successful characters endpoint"""
        url = reverse("app:characters-list")
        response = self.client.get(url)
        data = response.data["results"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 2)

    def test_get_characters_filtered(self):
        """Test characters endpoint with name filter"""
        url = reverse("app:characters-list") + "?contains=skywalker"
        response = self.client.get(url)
        data = response.data["results"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Luke Skywalker")


class StarshipViewSetTest(APITestCase):
    def setUp(self):
        self.starship1 = models.Starship.objects.create(
            name="Millennium Falcon",
            model="YT-1300 light freighter",
            cost_in_credits=100000,
            hyperdrive_rating=0.5,
            swapi_url="https://swapi.info/api/starships/2/",
        )
        self.starship2 = models.Starship.objects.create(
            name="X-wing",
            model="T-65 X-wing",
            cost_in_credits=149999,
            hyperdrive_rating=1.0,
            swapi_url="https://swapi.info/api/starships/3",
        )

    def test_get_starships_success(self):
        """Test successful starships endpoint"""
        url = reverse("app:starships-list")
        response = self.client.get(url)
        data = response.data["results"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 2)

    def test_get_starships_filtered(self):
        """Test starships endpoint with name filter"""
        url = reverse("app:starships-list") + "?contains=wing"
        response = self.client.get(url)
        data = response.data["results"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "X-wing")


class EmptyDatabaseTest(APITestCase):
    def test_empty_films(self):
        """Test films endpoint with empty database"""
        url = reverse("app:films-list")
        response = self.client.get(url)
        data = response.data["results"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, [])

    def test_empty_characters(self):
        """Test characters endpoint with empty database"""
        url = reverse("app:characters-list")
        response = self.client.get(url)
        data = response.data["results"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, [])

    def test_empty_starships(self):
        """Test starships endpoint with empty database"""
        url = reverse("app:starships-list")
        response = self.client.get(url)
        data = response.data["results"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, [])
