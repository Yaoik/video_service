from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TitleView


router = DefaultRouter()
router.register(r'titles', TitleView, basename='title')

urlpatterns = [
    path('', include(router.urls)),
]
