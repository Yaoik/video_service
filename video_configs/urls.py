from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VideoConfigViewSet


router = DefaultRouter()
router.register(r'video_configs', VideoConfigViewSet, basename='video_config')

urlpatterns = [
    path('', include(router.urls)),
]
