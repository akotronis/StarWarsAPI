from django.db import models
from psqlextra.manager import PostgresManager
from psqlextra.models import PostgresPartitionedModel
from psqlextra.types import PostgresPartitioningMethod

from . import constants


class CommonFieldsAbstractModel(models.Model):
    INTERNAL_FIELDS = ["created_at", "updated_at"]

    swapi_url = models.URLField(blank=True, null=True)
    swapi_id = models.BigIntegerField(
        blank=True, null=True, db_index=True, help_text="The resource id on swapi data"
    )
    created = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PostgresManager()

    class Meta:
        abstract = True

    @classmethod
    def get_deserialized_fields(cls):
        return [
            f.name
            for f in cls._meta.fields
            if not any([f.primary_key, f.name in cls.INTERNAL_FIELDS])
        ]

    @classmethod
    def get_many_to_many_fieldname(cls):
        return next(iter(cls._meta.many_to_many)).name

    @classmethod
    def get_many_to_many_related_model_table_name(cls):
        return next(iter(cls._meta.many_to_many)).remote_field.model._meta.db_table


class Film(CommonFieldsAbstractModel):
    title = models.CharField(blank=True, max_length=500)
    episode_id = models.IntegerField(blank=True, null=True)
    director = models.CharField(blank=True, max_length=100)
    release_date = models.DateField(blank=True, null=True)
    starships = models.ManyToManyField("Starship", blank=True, related_name="films")

    def __str__(self):
        return f"({self.pk}) Title: {self.title}, Director: {self.director}, Release date: {self.release_date}"


class Character(CommonFieldsAbstractModel):
    name = models.CharField(blank=True, max_length=100)
    height = models.FloatField(blank=True, null=True)
    gender = models.CharField(blank=True, max_length=50)
    films = models.ManyToManyField(Film, blank=True, related_name="characters")

    def __str__(self):
        return f"({self.pk}) Name: {self.name}, Gender: {self.gender}, Height: {self.height}"


class Starship(CommonFieldsAbstractModel):
    name = models.CharField(blank=True, max_length=100)
    model = models.CharField(blank=True, max_length=500)
    cost_in_credits = models.BigIntegerField(blank=True, null=True)
    hyperdrive_rating = models.FloatField(blank=True, null=True)
    characters = models.ManyToManyField(Character, blank=True, related_name="starships")

    def __str__(self):
        return f"({self.pk}) Name: {self.name}, Model: {self.model}"


class StagedRelationship(PostgresPartitionedModel):
    """
    Intermediate model holding relationships between resource swapi ids.
    Used to avoid keeping mappings defining resource relationships in memory.
    Instead, store them here in bulk and use this table to create the through tables
    between entities by joining this table with the entities tables.
    Index the swapi ids for faster joins.
    """

    from_type = models.CharField(max_length=20, choices=constants.ResourceEnum.choices)
    from_swapi_id = models.BigIntegerField(db_index=True)
    to_type = models.CharField(max_length=20, choices=constants.ResourceEnum.choices)
    to_swapi_id = models.BigIntegerField(db_index=True)

    class PartitioningMeta:
        method = PostgresPartitioningMethod.LIST
        key = ["from_type"]
