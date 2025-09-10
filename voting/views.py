from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.db.models import F, Sum
from drf_spectacular.utils import extend_schema
from .models import Vote
from .serializers import VoteSerializer, VoteStatsSerializer
from core.models import Character, Film, Starship
import logging

logger = logging.getLogger(__name__)

from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

@extend_schema(tags=['Voting'])
class VoteViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['vote_type']
    ordering_fields = ['votes', 'created_at']
    ordering = ['-votes']

    @extend_schema(
        summary="List all votes",
        description="Retrieve a paginated list of all votes with filtering and ordering capabilities."
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Cast a vote",
        description="Cast a vote for a character, film, or starship. If a vote already exists for the item, the vote count will be incremented."
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vote_type = serializer.validated_data['vote_type']
        item_id = serializer.validated_data['item_id']
        vote, created = Vote.objects.get_or_create(
            vote_type=vote_type, item_id=item_id, defaults={'votes': 1}
        )
        if not created:
            vote.votes = F('votes') + 1
            vote.save(update_fields=['votes'])
            vote.refresh_from_db()
        serializer = self.get_serializer(vote)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Get enhanced voting statistics",
        description="Get comprehensive voting statistics with percentages and item names for each category, perfect for graph visualization.",
        responses=VoteStatsSerializer
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        try:
            # Get vote totals per category
            character_votes = Vote.objects.filter(vote_type='character')
            film_votes = Vote.objects.filter(vote_type='film')
            starship_votes = Vote.objects.filter(vote_type='starship')
            
            character_total = character_votes.aggregate(total=Sum('votes'))['total'] or 0
            film_total = film_votes.aggregate(total=Sum('votes'))['total'] or 0
            starship_total = starship_votes.aggregate(total=Sum('votes'))['total'] or 0
            overall_total = character_total + film_total + starship_total
            
            # Get top characters with details
            top_character_votes = character_votes.order_by('-votes')[:10]
            character_stats = []
            for vote in top_character_votes:
                try:
                    character = Character.objects.get(id=vote.item_id)
                    percentage = (vote.votes / character_total * 100) if character_total > 0 else 0
                    character_stats.append({
                        'id': vote.item_id,
                        'name': character.name,
                        'votes': vote.votes,
                        'percentage': round(percentage, 2)
                    })
                except Character.DoesNotExist:
                    continue
            
            # Get top films with details
            top_film_votes = film_votes.order_by('-votes')[:10]
            film_stats = []
            for vote in top_film_votes:
                try:
                    film = Film.objects.get(id=vote.item_id)
                    percentage = (vote.votes / film_total * 100) if film_total > 0 else 0
                    film_stats.append({
                        'id': vote.item_id,
                        'name': film.title,
                        'votes': vote.votes,
                        'percentage': round(percentage, 2)
                    })
                except Film.DoesNotExist:
                    continue
            
            # Get top starships with details
            top_starship_votes = starship_votes.order_by('-votes')[:10]
            starship_stats = []
            for vote in top_starship_votes:
                try:
                    starship = Starship.objects.get(id=vote.item_id)
                    percentage = (vote.votes / starship_total * 100) if starship_total > 0 else 0
                    starship_stats.append({
                        'id': vote.item_id,
                        'name': starship.name,
                        'votes': vote.votes,
                        'percentage': round(percentage, 2)
                    })
                except Starship.DoesNotExist:
                    continue
            
            stats_data = {
                'characters': {
                    'total_votes': character_total,
                    'top_items': character_stats
                },
                'films': {
                    'total_votes': film_total,
                    'top_items': film_stats
                },
                'starships': {
                    'total_votes': starship_total,
                    'top_items': starship_stats
                },
                'overall_total': overall_total
            }
            
            return Response(stats_data)
            
        except Exception as e:
            logger.error(f"Error getting vote statistics: {e}")
            return Response({
                'error': 'Failed to retrieve voting statistics'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
