from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CharacterViewSet, FilmViewSet, StarshipViewSet, SWAPIViewSet

router = DefaultRouter()
router.register(r'characters', CharacterViewSet, basename='characters')
router.register(r'films', FilmViewSet, basename='films')
router.register(r'starships', StarshipViewSet, basename='starships')
router.register(r'swapi', SWAPIViewSet, basename='swapi')

urlpatterns = [
    path('', include(router.urls)),
]
