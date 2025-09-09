from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VoteViewSet

router = DefaultRouter()
router.register(r'votes', VoteViewSet, basename='votes')

urlpatterns = [
    path('', include(router.urls)),
]
