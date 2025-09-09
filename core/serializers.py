from rest_framework import serializers
from .models import Character, Film, Starship, DataSyncStatus

class FilmSerializer(serializers.ModelSerializer):
    characters_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Film
        fields = [
            'id', 'swapi_id', 'title', 'episode_id', 'opening_crawl', 
            'director', 'producer', 'release_date', 'characters_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'swapi_id', 'created_at', 'updated_at']
    
    def get_characters_count(self, obj):
        return obj.characters.count()

class StarshipSerializer(serializers.ModelSerializer):
    pilots_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Starship
        fields = [
            'id', 'swapi_id', 'name', 'model', 'manufacturer', 'cost_in_credits',
            'length', 'max_atmosphering_speed', 'crew', 'passengers', 
            'cargo_capacity', 'hyperdrive_rating', 'starship_class',
            'pilots_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'swapi_id', 'created_at', 'updated_at']
    
    def get_pilots_count(self, obj):
        return obj.pilots.count()

class CharacterSerializer(serializers.ModelSerializer):
    films = FilmSerializer(many=True, read_only=True)
    starships = StarshipSerializer(many=True, read_only=True)
    films_count = serializers.SerializerMethodField()
    starships_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Character
        fields = [
            'id', 'swapi_id', 'name', 'height', 'mass', 'hair_color',
            'skin_color', 'eye_color', 'birth_year', 'gender',
            'films', 'starships', 'films_count', 'starships_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'swapi_id', 'created_at', 'updated_at']
    
    def get_films_count(self, obj):
        return obj.films.count()
    
    def get_starships_count(self, obj):
        return obj.starships.count()

class CharacterListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    films_count = serializers.SerializerMethodField()
    starships_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Character
        fields = [
            'id', 'swapi_id', 'name', 'height', 'mass', 'gender','hair_color',
            'films_count', 'starships_count', 'created_at'
        ]
    
    def get_films_count(self, obj):
        return obj.films.count()
    
    def get_starships_count(self, obj):
        return obj.starships.count()


class DataSyncStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSyncStatus
        fields = '__all__'
