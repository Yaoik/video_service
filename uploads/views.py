#from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.generics import mixins
from .models import Video
from .serializers import VideoSerializer
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from hls.tasks import process_video
from rest_framework.serializers import ValidationError
from .filters import VideoFilter
import django_filters



class VideoView(
        GenericViewSet,
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.DestroyModelMixin,
    ):
    queryset = Video.objects.all().order_by('-id')
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]

    filterset_class = VideoFilter
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    
    def perform_create(self, serializer:VideoSerializer):
        validated_data = serializer.validated_data
        assert isinstance(validated_data, dict)
        title = validated_data.get('title')
        moderated = title is not None

        video = serializer.save(
            user=self.request.user,
            moderated=moderated,
        )

        process_video.delay(video.id)
        
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return response