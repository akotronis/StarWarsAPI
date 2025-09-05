from rest_framework import serializers

from . import mixins
from . import models

class FilmSerializer(serializers.ModelSerializer):
    characters = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = models.Film
        fields = '__all__'


class CharacterSerializer(serializers.ModelSerializer):
    films = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    
    class Meta:
        model = models.Character
        fields = '__all__'


class StarshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Starship
        fields = '__all__'


class SWAPIFilmSerializer(serializers.Serializer):
    title = serializers.CharField(required=False)
    episode_id = serializers.IntegerField(required=False)
    director = serializers.CharField(required=False)
    release_date = serializers.DateField(required=False)
    created = serializers.DateTimeField(required=False)
    url = serializers.URLField(required=False, source='swapi_url')
    starships = serializers.ListField(child=serializers.URLField(), required=False)


class SWAPICharacterSerializer(mixins.HandleNumericsSerializerMixin, serializers.Serializer):
    numeric_fields_as_strings = ['height'] 

    name = serializers.CharField(required=False)
    height = serializers.FloatField(required=False, allow_null=True)
    gender = serializers.CharField(required=False)
    created = serializers.DateTimeField(required=False)
    url = serializers.URLField(required=False, source='swapi_url')
    films = serializers.ListField(child=serializers.URLField(), required=False)


class SWAPIStarshipSerializer(mixins.HandleNumericsSerializerMixin, serializers.Serializer):
    numeric_fields_as_strings = ['cost_in_credits', 'hyperdrive_rating'] 

    name = serializers.CharField(required=False)
    model = serializers.CharField(required=False)
    cost_in_credits = serializers.IntegerField(required=False, allow_null=True)
    hyperdrive_rating = serializers.FloatField(required=False, allow_null=True)
    created = serializers.DateTimeField(required=False)
    url = serializers.URLField(required=False, source='swapi_url')
    pilots = serializers.ListField(child=serializers.URLField(), required=False, source='characters')