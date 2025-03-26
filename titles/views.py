#from rest_framework.views import APIView
#from rest_framework.response import Response
#from rest_framework import status
from rest_framework.generics import mixins
from .models import Title
from .serializers import TitleSerializer
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from .filters import TitleFilter
import django_filters

class TitleView(
        GenericViewSet,
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
    ):
    queryset = Title.objects.all().order_by('-id')
    serializer_class = TitleSerializer
    permission_classes = [AllowAny]
    
    filterset_class = TitleFilter
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]