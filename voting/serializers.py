from rest_framework import serializers
from .models import Vote
from core.models import Character, Film, Starship

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['id', 'vote_type', 'item_id', 'votes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'votes', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        vote_type = attrs.get('vote_type')
        item_id = attrs.get('item_id')
        
        # Validate that the item exists
        if vote_type == 'character':
            if not Character.objects.filter(id=item_id).exists():
                raise serializers.ValidationError("Character with this ID does not exist.")
        elif vote_type == 'film':
            if not Film.objects.filter(id=item_id).exists():
                raise serializers.ValidationError("Film with this ID does not exist.")
        elif vote_type == 'starship':
            if not Starship.objects.filter(id=item_id).exists():
                raise serializers.ValidationError("Starship with this ID does not exist.")
        
        return attrs

class VoteStatsItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    votes = serializers.IntegerField()
    percentage = serializers.FloatField()

class VoteStatsCategorySerializer(serializers.Serializer):
    total_votes = serializers.IntegerField()
    top_items = VoteStatsItemSerializer(many=True)

class VoteStatsSerializer(serializers.Serializer):
    characters = VoteStatsCategorySerializer()
    films = VoteStatsCategorySerializer()
    starships = VoteStatsCategorySerializer()
    overall_total = serializers.IntegerField()
