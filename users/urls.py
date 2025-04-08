from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserView


urlpatterns = [
    path('me/', UserView.as_view(), name='user-view'),
]
