#from rest_framework.views import APIView
#from rest_framework.response import Response
#from rest_framework import status
from rest_framework.generics import mixins
from .models import Title
from .serializers import TitleSerializer
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny



class TitleView(
        GenericViewSet,
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
    ):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = [AllowAny]