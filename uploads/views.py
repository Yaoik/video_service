#from rest_framework.views import APIView
#from rest_framework.response import Response
#from rest_framework import status
from rest_framework.generics import mixins
from .models import Video
from .serializers import VideoSerializer
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated


class VideoView(mixins.ListModelMixin, GenericViewSet, mixins.CreateModelMixin):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer: VideoSerializer):
        serializer.save(user=self.request.user)