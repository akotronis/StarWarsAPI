from rest_framework import serializers

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
    starships = serializers.ListField(child=serializers.URLField(), required=False)


class SWAPICharacterSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    height = serializers.FloatField(required=False)
    gender = serializers.CharField(required=False)
    created = serializers.DateTimeField(required=False)
    films = serializers.ListField(child=serializers.URLField(), required=False)


class SWAPIStarshipSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    model = serializers.CharField(required=False)
    cost_in_credits = serializers.IntegerField(required=False)
    hyperdrive_rating = serializers.FloatField(required=False)
    created = serializers.DateTimeField(required=False)
    character = serializers.URLField(required=False)
