from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import F
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .models import Character, Film, Starship, DataSyncStatus
from .serializers import (
    CharacterSerializer, CharacterListSerializer,
    FilmSerializer, StarshipSerializer,
    DataSyncStatusSerializer
)
from .services import SWAPIService, SWAPIError
import logging

logger = logging.getLogger(__name__)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ReadOnlyBaseViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    pass

@extend_schema(tags=['Characters'])
class CharacterViewSet(ReadOnlyBaseViewSet):
    queryset = Character.objects.all().prefetch_related('films', 'starships')
    serializer_class = CharacterSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['gender', 'eye_color', 'hair_color']
    search_fields = ['name', 'hair_color', 'eye_color']
    ordering_fields = ['name', 'height', 'mass', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'list':
            return CharacterListSerializer
        return CharacterSerializer

    @extend_schema(
        summary="List all characters",
        description="Retrieve a paginated list of Star Wars characters with filtering, searching, and ordering capabilities.",
        parameters=[
            OpenApiParameter(
                name='ordering',
                description='Order results by specified fields. Available fields: name, height, mass, created_at. Use "-" prefix for descending order.',
                required=False,
                type=OpenApiTypes.STR,
                examples=[
                    OpenApiExample('Sort by name (A-Z)', value='name'),
                    OpenApiExample('Sort by name (Z-A)', value='-name'),
                    OpenApiExample('Sort by height (low to high)', value='height'),
                    OpenApiExample('Sort by creation date (newest first)', value='-created_at'),
                ]
            ),
            OpenApiParameter(
                name='search',
                description='Search characters by name, hair color, or eye color (case-insensitive partial matching).',
                required=False,
                type=OpenApiTypes.STR,
                examples=[
                    OpenApiExample('Search by name', value='Luke'),
                    OpenApiExample('Search by hair color', value='brown'),
                    OpenApiExample('Search by eye color', value='blue'),
                ]
            ),
            OpenApiParameter(
                name='gender',
                description='Filter by gender.',
                required=False,
                type=OpenApiTypes.STR,
                examples=[
                    OpenApiExample('Male characters', value='male'),
                    OpenApiExample('Female characters', value='female'),
                ]
            ),
            OpenApiParameter(
                name='eye_color',
                description='Filter by eye color.',
                required=False,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name='hair_color',
                description='Filter by hair color.',
                required=False,
                type=OpenApiTypes.STR,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Get character details",
        description="Retrieve detailed information about a specific Star Wars character including related films and starships."
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Search characters by name",
        description="Search for characters by name using substring matching.",
        parameters=[
            OpenApiParameter(
                name='q',
                description='Search query string to match against character names.',
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                examples=[
                    OpenApiExample('Search for Luke', value='luke'),
                    OpenApiExample('Search for Darth', value='darth'),
                    OpenApiExample('Search for Skywalker', value='skywalker'),
                ]
            ),
        ]
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        q = request.GET.get('q', '')
        if not q:
            return Response({'error': 'Query parameter "q" is required'}, status=status.HTTP_400_BAD_REQUEST)
        queryset = self.queryset.filter(name__icontains=q)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page or queryset, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

@extend_schema(tags=['Films'])
class FilmViewSet(ReadOnlyBaseViewSet):
    queryset = Film.objects.all().prefetch_related('characters')
    serializer_class = FilmSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['episode_id', 'director']
    search_fields = ['title', 'director', 'opening_crawl']
    ordering_fields = ['title', 'episode_id', 'release_date', 'created_at']
    ordering = ['episode_id']

    @extend_schema(
        summary="List all films",
        description="Retrieve a paginated list of Star Wars films with filtering, searching, and ordering capabilities.",
        parameters=[
            OpenApiParameter(
                name='ordering',
                description='Order results by specified fields. Available fields: title, episode_id, release_date, created_at. Use "-" prefix for descending order.',
                required=False,
                type=OpenApiTypes.STR,
                examples=[
                    OpenApiExample('Sort by episode (1-6)', value='episode_id'),
                    OpenApiExample('Sort by episode (6-1)', value='-episode_id'),
                    OpenApiExample('Sort by title (A-Z)', value='title'),
                    OpenApiExample('Sort by release date (newest first)', value='-release_date'),
                ]
            ),
            OpenApiParameter(
                name='search',
                description='Search films by title, director, or opening crawl text (case-insensitive partial matching).',
                required=False,
                type=OpenApiTypes.STR,
                examples=[
                    OpenApiExample('Search by title', value='Empire'),
                    OpenApiExample('Search by director', value='Lucas'),
                    OpenApiExample('Search in opening crawl', value='Death Star'),
                ]
            ),
            OpenApiParameter(
                name='episode_id',
                description='Filter by episode number.',
                required=False,
                type=OpenApiTypes.INT,
                examples=[
                    OpenApiExample('Episode IV', value=4),
                    OpenApiExample('Episode V', value=5),
                ]
            ),
            OpenApiParameter(
                name='director',
                description='Filter by director name.',
                required=False,
                type=OpenApiTypes.STR,
                examples=[
                    OpenApiExample('George Lucas films', value='George Lucas'),
                ]
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Get film details",
        description="Retrieve detailed information about a specific Star Wars film including related characters."
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Search films by title",
        description="Search for films by title using substring matching.",
        parameters=[
            OpenApiParameter(
                name='q',
                description='Search query string to match against film titles.',
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                examples=[
                    OpenApiExample('Search for Empire', value='empire'),
                    OpenApiExample('Search for Hope', value='hope'),
                    OpenApiExample('Search for Jedi', value='jedi'),
                ]
            ),
        ]
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        q = request.GET.get('q', '')
        if not q:
            return Response({'error': 'Query parameter "q" is required'}, status=status.HTTP_400_BAD_REQUEST)
        queryset = self.queryset.filter(title__icontains=q)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page or queryset, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

@extend_schema(tags=['Starships'])
class StarshipViewSet(ReadOnlyBaseViewSet):
    queryset = Starship.objects.all().prefetch_related('pilots')
    serializer_class = StarshipSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['starship_class', 'manufacturer']
    search_fields = ['name', 'model', 'manufacturer']
    ordering_fields = ['name', 'length', 'created_at']
    ordering = ['name']

    @extend_schema(
        summary="List all starships",
        description="Retrieve a paginated list of Star Wars starships with filtering, searching, and ordering capabilities.",
        parameters=[
            OpenApiParameter(
                name='ordering',
                description='Order results by specified fields. Available fields: name, length, created_at. Use "-" prefix for descending order.',
                required=False,
                type=OpenApiTypes.STR,
                examples=[
                    OpenApiExample('Sort by name (A-Z)', value='name'),
                    OpenApiExample('Sort by name (Z-A)', value='-name'),
                    OpenApiExample('Sort by length', value='length'),
                    OpenApiExample('Sort by creation date (newest first)', value='-created_at'),
                ]
            ),
            OpenApiParameter(
                name='search',
                description='Search starships by name, model, or manufacturer (case-insensitive partial matching).',
                required=False,
                type=OpenApiTypes.STR,
                examples=[
                    OpenApiExample('Search by name', value='Falcon'),
                    OpenApiExample('Search by model', value='X-wing'),
                    OpenApiExample('Search by manufacturer', value='Corellian'),
                ]
            ),
            OpenApiParameter(
                name='starship_class',
                description='Filter by starship class.',
                required=False,
                type=OpenApiTypes.STR,
                examples=[
                    OpenApiExample('Starfighters', value='Starfighter'),
                    OpenApiExample('Light freighters', value='Light freighter'),
                ]
            ),
            OpenApiParameter(
                name='manufacturer',
                description='Filter by manufacturer.',
                required=False,
                type=OpenApiTypes.STR,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Get starship details",
        description="Retrieve detailed information about a specific Star Wars starship including technical specifications."
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Search starships by name",
        description="Search for starships by name using substring matching.",
        parameters=[
            OpenApiParameter(
                name='q',
                description='Search query string to match against starship names.',
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                examples=[
                    OpenApiExample('Search for Falcon', value='falcon'),
                    OpenApiExample('Search for X-wing', value='x-wing'),
                    OpenApiExample('Search for Destroyer', value='destroyer'),
                ]
            ),
        ]
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        q = request.GET.get('q', '')
        if not q:
            return Response({'error': 'Query parameter "q" is required'}, status=status.HTTP_400_BAD_REQUEST)
        queryset = self.queryset.filter(name__icontains=q)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page or queryset, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)


@extend_schema(tags=['SWAPI Integration'])
class SWAPIViewSet(viewsets.ViewSet):

    @extend_schema(
        summary="Populate all SWAPI data",
        description="Fetch and store all Star Wars data from SWAPI (characters, films, starships) into the local database."
    )
    @action(detail=False, methods=['post'])
    def populate_all(self, request):
        try:
            result = SWAPIService.populate_all_data()
            return Response({
                **result, 
                'success': True, 
                'message': 'Data population completed successfully'
            }, status=status.HTTP_200_OK)
        except SWAPIError as e:
            return Response({
                'success': False, 
                'error': str(e)
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            return Response({
                'success': False, 
                'error': 'Internal server error during data population'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Get synchronization status",
        description="Get the current synchronization status for all SWAPI resources including last sync time and record counts."
    )
    @action(detail=False, methods=['get'])
    def sync_status(self, request):
        try:
            statuses = DataSyncStatus.objects.all()
            serializer = DataSyncStatusSerializer(statuses, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving sync status: {e}")
            return Response({
                'error': 'Failed to retrieve synchronization status'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
