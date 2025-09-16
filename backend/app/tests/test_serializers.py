from django.test import TestCase

from .. import serializers


class SWAPIFilmSerializerTest(TestCase):
    def test_film_serializer_valid_data(self):
        """Test SWAPIFilmSerializer with valid data"""
        data = {
            "title": "A New Hope",
            "episode_id": 4,
            "director": "George Lucas",
            "release_date": "1977-05-25",
            "created": "2014-12-10T14:23:31.880000Z",
            "url": "https://swapi.info/api/films/1/",
            "starships": [
                "https://swapi.info/api/starships/2/",
                "https://swapi.info/api/starships/3/",
                "https://swapi.info/api/starships/5/",
            ],
        }
        serializer = serializers.SWAPIFilmSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["title"], "A New Hope")
        self.assertEqual(serializer.validated_data["episode_id"], 4)
        self.assertEqual(
            serializer.validated_data["swapi_url"], "https://swapi.info/api/films/1/"
        )
        self.assertEqual(
            serializer.validated_data["starships"],
            [
                "https://swapi.info/api/starships/2/",
                "https://swapi.info/api/starships/3/",
                "https://swapi.info/api/starships/5/",
            ],
        )

    def test_film_serializer_empty_starships(self):
        """Test SWAPIFilmSerializer with empty starships list"""
        data = {"title": "The Phantom Menace", "episode_id": 1, "starships": []}
        serializer = serializers.SWAPIFilmSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["starships"], [])

    def test_film_serializer_missing_starships(self):
        """Test SWAPIFilmSerializer with missing starships field"""
        data = {"title": "Attack of the Clones", "episode_id": 2}
        serializer = serializers.SWAPIFilmSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertNotIn("starships", serializer.validated_data)

    def test_film_serializer_source_mapping(self):
        """Test that url field maps to swapi_url"""
        data = {"title": "Test Film", "url": "https://swapi.info/api/films/99/"}
        serializer = serializers.SWAPIFilmSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data["swapi_url"], "https://swapi.info/api/films/99/"
        )


class SWAPICharacterSerializerTest(TestCase):
    def test_character_serializer_valid_data(self):
        """Test SWAPICharacterSerializer with valid data"""
        data = {
            "name": "Luke Skywalker",
            "height": "172",
            "gender": "male",
            "created": "2014-12-09T13:50:51.644000Z",
            "url": "https://swapi.info/api/people/1/",
            "films": [
                "https://swapi.info/api/films/1/",
                "https://swapi.info/api/films/2/",
                "https://swapi.info/api/films/3/",
            ],
        }
        serializer = serializers.SWAPICharacterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["name"], "Luke Skywalker")
        self.assertEqual(serializer.validated_data["height"], 172.0)
        self.assertEqual(
            serializer.validated_data["swapi_url"], "https://swapi.info/api/people/1/"
        )
        self.assertEqual(
            serializer.validated_data["films"],
            [
                "https://swapi.info/api/films/1/",
                "https://swapi.info/api/films/2/",
                "https://swapi.info/api/films/3/",
            ],
        )

    def test_character_serializer_unknown_height(self):
        """Test SWAPICharacterSerializer handles 'unknown' height"""
        data = {
            "name": "Darth Vader",
            "height": "unknown",
            "gender": "male",
            "films": ["https://swapi.info/api/films/1/"],
        }
        serializer = serializers.SWAPICharacterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertIsNone(serializer.validated_data["height"])
        self.assertEqual(
            serializer.validated_data["films"], ["https://swapi.info/api/films/1/"]
        )

    def test_character_serializer_empty_films(self):
        """Test SWAPICharacterSerializer with empty films list"""
        data = {
            "name": "Jabba the Hutt",
            "height": "175",
            "gender": "hermaphrodite",
            "films": [],  # Empty list
        }
        serializer = serializers.SWAPICharacterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["films"], [])

    def test_character_serializer_source_mapping(self):
        """Test that url field maps to swapi_url"""
        data = {
            "name": "Test Character",
            "url": "https://swapi.info/api/people/99/",
            "films": ["https://swapi.info/api/films/1/"],
        }
        serializer = serializers.SWAPICharacterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data["swapi_url"], "https://swapi.info/api/people/99/"
        )
        self.assertEqual(
            serializer.validated_data["films"], ["https://swapi.info/api/films/1/"]
        )


class SWAPIStarshipSerializerTest(TestCase):
    def test_starship_serializer_valid_data(self):
        """Test SWAPIStarshipSerializer with valid data"""
        data = {
            "name": "Millennium Falcon",
            "model": "YT-1300 light freighter",
            "cost_in_credits": "100000",
            "hyperdrive_rating": "0.5",
            "created": "2014-12-10T16:59:45.094000Z",
            "url": "https://swapi.info/api/starships/10/",
            "pilots": [
                "https://swapi.info/api/people/13/",
                "https://swapi.info/api/people/14/",
            ],
        }
        serializer = serializers.SWAPIStarshipSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["name"], "Millennium Falcon")
        self.assertEqual(serializer.validated_data["cost_in_credits"], 100000)
        self.assertEqual(serializer.validated_data["hyperdrive_rating"], 0.5)
        self.assertEqual(
            serializer.validated_data["swapi_url"],
            "https://swapi.info/api/starships/10/",
        )

    def test_starship_serializer_unknown_cost(self):
        """Test SWAPIStarshipSerializer handles 'unknown' cost_in_credits"""
        data = {
            "name": "Death Star",
            "model": "DS-1 Orbital Battle Station",
            "cost_in_credits": "unknown",
            "hyperdrive_rating": "4.0",
        }
        serializer = serializers.SWAPIStarshipSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertIsNone(serializer.validated_data["cost_in_credits"])
        self.assertEqual(serializer.validated_data["hyperdrive_rating"], 4.0)

    def test_starship_serializer_unknown_hyperdrive(self):
        """Test SWAPIStarshipSerializer handles 'unknown' hyperdrive_rating"""
        data = {
            "name": "Sentinel-class landing craft",
            "model": "Sentinel-class landing craft",
            "cost_in_credits": "240000",
            "hyperdrive_rating": "unknown",
        }
        serializer = serializers.SWAPIStarshipSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["cost_in_credits"], 240000)
        self.assertIsNone(serializer.validated_data["hyperdrive_rating"])

    def test_starship_serializer_both_unknown_values(self):
        """Test SWAPIStarshipSerializer handles both unknown cost and hyperdrive"""
        data = {
            "name": "Theta-class T-2c shuttle",
            "model": "Theta-class T-2c shuttle",
            "cost_in_credits": "unknown",
            "hyperdrive_rating": "unknown",
        }
        serializer = serializers.SWAPIStarshipSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertIsNone(serializer.validated_data["cost_in_credits"])
        self.assertIsNone(serializer.validated_data["hyperdrive_rating"])

    def test_starship_serializer_missing_optional_fields(self):
        """Test SWAPIStarshipSerializer with missing optional fields"""
        data = {"name": "X-Wing", "model": "T-65 X-wing"}
        serializer = serializers.SWAPIStarshipSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["name"], "X-Wing")
        self.assertNotIn("cost_in_credits", serializer.validated_data)
        self.assertNotIn("hyperdrive_rating", serializer.validated_data)

    def test_starship_serializer_empty_pilots(self):
        """Test SWAPIStarshipSerializer with empty pilots list"""
        data = {
            "name": "Death Star",
            "model": "DS-1 Orbital Battle Station",
            "cost_in_credits": "1000000000000",
            "hyperdrive_rating": "4.0",
            "pilots": [],
        }
        serializer = serializers.SWAPIStarshipSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["characters"], [])

    def test_starship_serializer_source_mapping(self):
        """Test that url field maps to swapi_url and pilots to characters"""
        data = {
            "name": "Millennium Falcon",
            "url": "https://swapi.info/api/starships/10/",
            "pilots": ["https://swapi.info/api/people/13/"],
        }
        serializer = serializers.SWAPIStarshipSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data["swapi_url"],
            "https://swapi.info/api/starships/10/",
        )
        self.assertEqual(
            serializer.validated_data["characters"],
            ["https://swapi.info/api/people/13/"],
        )

    def test_starship_serializer_invalid_hyperdrive_rating(self):
        """Test SWAPIStarshipSerializer with invalid hyperdrive_rating"""
        data = {
            "name": "Test Ship",
            "model": "Test Model",
            "hyperdrive_rating": "not_a_number",
        }
        serializer = serializers.SWAPIStarshipSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("hyperdrive_rating", serializer.errors)

    def test_starship_serializer_invalid_cost_in_credits(self):
        """Test SWAPIStarshipSerializer with invalid cost_in_credits"""
        data = {
            "name": "Test Ship",
            "model": "Test Model",
            "cost_in_credits": "not_a_number",
        }
        serializer = serializers.SWAPIStarshipSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("cost_in_credits", serializer.errors)
