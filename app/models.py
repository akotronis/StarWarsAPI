from django.db import models


class Film(models.Model):
    title = models.CharField(blank=True, max_length=500)
    episode_id = models.IntegerField(blank=True, null=True)
    director = models.CharField(blank=True, max_length=100)
    release_date = models.DateField(blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)
    swapi_url = models.URLField(blank=True, null=True)
    starships = models.ManyToManyField("Starship", blank=True, related_name="films")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"({self.pk}) Title: {self.title}, Director: {self.director}, Release date: {self.release_date}"


class Character(models.Model):
    name = models.CharField(blank=True, max_length=100)
    height = models.FloatField(blank=True, null=True)
    gender = models.CharField(blank=True, max_length=50)
    created = models.DateTimeField(blank=True, null=True)
    swapi_url = models.URLField(blank=True, null=True)
    films = models.ManyToManyField(Film, blank=True, related_name="characters")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"({self.pk}) Name: {self.name}, Gender: {self.gender}, Height: {self.height}"


class Starship(models.Model):
    name = models.CharField(blank=True, max_length=100)
    model = models.CharField(blank=True, max_length=500)
    cost_in_credits = models.BigIntegerField(blank=True, null=True)
    hyperdrive_rating = models.FloatField(blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)
    swapi_url = models.URLField(blank=True, null=True)
    characters = models.ManyToManyField(Character, blank=True, related_name="starships")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"({self.pk}) Name: {self.name}, Model: {self.model}"
