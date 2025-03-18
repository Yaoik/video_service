from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VideoView


router = DefaultRouter()
router.register(r'videos', VideoView, basename='video')

urlpatterns = [
    path('', include(router.urls)),
]
