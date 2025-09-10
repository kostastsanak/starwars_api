from django.db import models

class BaseModel(models.Model):
    """Base model with common fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class Film(BaseModel):
    swapi_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=255, db_index=True)
    episode_id = models.IntegerField()
    opening_crawl = models.TextField()
    director = models.CharField(max_length=255)
    producer = models.CharField(max_length=255)
    release_date = models.DateField()
    
    class Meta:
        ordering = ['episode_id']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['episode_id']),
        ]
    
    def __str__(self):
        return f"Episode {self.episode_id}: {self.title}"

class Starship(BaseModel):
    swapi_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255, db_index=True)
    model = models.CharField(max_length=255)
    manufacturer = models.CharField(max_length=255)
    cost_in_credits = models.CharField(max_length=50, null=True, blank=True)
    length = models.CharField(max_length=50, null=True, blank=True)
    max_atmosphering_speed = models.CharField(max_length=50, null=True, blank=True)
    crew = models.CharField(max_length=50, null=True, blank=True)
    passengers = models.CharField(max_length=50, null=True, blank=True)
    cargo_capacity = models.CharField(max_length=50, null=True, blank=True)
    hyperdrive_rating = models.CharField(max_length=50, null=True, blank=True)
    starship_class = models.CharField(max_length=255)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['starship_class']),
        ]
    
    def __str__(self):
        return self.name

class Character(BaseModel):
    swapi_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255, db_index=True)
    height = models.CharField(max_length=10, null=True, blank=True)
    mass = models.CharField(max_length=10, null=True, blank=True)
    hair_color = models.CharField(max_length=50, null=True, blank=True)
    skin_color = models.CharField(max_length=50, null=True, blank=True)
    eye_color = models.CharField(max_length=50, null=True, blank=True)
    birth_year = models.CharField(max_length=20, null=True, blank=True)
    gender = models.CharField(max_length=50, null=True, blank=True)
    films = models.ManyToManyField(Film, related_name='characters', blank=True)
    starships = models.ManyToManyField(Starship, related_name='pilots', blank=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['gender']),
        ]
    
    def __str__(self):
        return self.name

class DataSyncStatus(BaseModel):
    """Track SWAPI data synchronization status"""
    resource_type = models.CharField(max_length=50, unique=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    total_records = models.IntegerField(default=0)
    is_syncing = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.resource_type}: {self.total_records} records"
