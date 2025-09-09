from django.db import models
from django.core.validators import MinValueValidator

class BaseModel(models.Model):
    """Base model with common fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class Vote(BaseModel):
    VOTE_TYPE_CHOICES = [
        ('character', 'Character'),
        ('film', 'Film'),
        ('starship', 'Starship'),
    ]
    
    vote_type = models.CharField(max_length=20, choices=VOTE_TYPE_CHOICES, db_index=True)
    item_id = models.PositiveIntegerField()
    votes = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    
    class Meta:
        unique_together = ('vote_type', 'item_id')
        indexes = [
            models.Index(fields=['vote_type', 'votes']),
        ]
        
    def __str__(self):
        return f"{self.get_vote_type_display()} {self.item_id}: {self.votes} votes"
