from django.contrib import admin
from .models import Character, Film, Starship, DataSyncStatus

@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ('name', 'gender', 'height', 'mass', 'birth_year', 'created_at')
    list_filter = ('gender', 'eye_color', 'hair_color')
    search_fields = ('name', 'gender')
    filter_horizontal = ('films', 'starships')
    readonly_fields = ('swapi_id', 'created_at', 'updated_at')

@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = ('title', 'episode_id', 'director', 'release_date', 'created_at')
    list_filter = ('director', 'release_date')
    search_fields = ('title', 'director')
    readonly_fields = ('swapi_id', 'created_at', 'updated_at')

@admin.register(Starship)
class StarshipAdmin(admin.ModelAdmin):
    list_display = ('name', 'model', 'manufacturer', 'starship_class', 'created_at')
    list_filter = ('starship_class', 'manufacturer')
    search_fields = ('name', 'model', 'manufacturer')
    readonly_fields = ('swapi_id', 'created_at', 'updated_at')

@admin.register(DataSyncStatus)
class DataSyncStatusAdmin(admin.ModelAdmin):
    list_display = ('resource_type', 'last_sync', 'total_records', 'is_syncing')
    list_filter = ('resource_type', 'is_syncing')
    readonly_fields = ('created_at', 'updated_at')
