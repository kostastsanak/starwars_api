from django.contrib import admin
from .models import Vote

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('vote_type', 'item_id', 'votes', 'created_at')
    list_filter = ('vote_type', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
