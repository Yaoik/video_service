from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import VideoConfig
from uploads.models import Video
from .serializers import VideoConfigSerializer, VideoSerializer
from django.core.files.uploadedfile import UploadedFile
from rest_framework.request import Request
from rest_framework.generics import mixins
from .serializers import VideoSerializer
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from hls.tasks import process_video
from .filters import VideoConfigFilter


class VideoConfigViewSet(viewsets.ModelViewSet):
    queryset = VideoConfig.objects.all()
    serializer_class = VideoConfigSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = VideoConfigFilter
    search_fields = ['title', ]
    ordering_fields = ['created_at', 'updated_at', 'video__size', 'video__duration']
    ordering = ['-created_at']
    
    lookup_field = 'uuid'
    lookup_url_kwarg = 'uuid'
    
    def get_queryset(self):
        return VideoConfig.objects.filter(user=self.request.user).prefetch_related('video__hls_videos')

    def perform_create(self, serializer:VideoConfigSerializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post', 'delete'], url_path='video')
    def video(self, request: Request, uuid:None|str=None) -> Response:
        if request.method == 'POST':
            return self.upload_video(request, uuid)
        elif request.method == 'DELETE':
            return self.delete_video(request, uuid)
        
        return Response(
            {"error": "Method not allowed"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        
    def upload_video(self, request:Request, uuid:None|str=None) -> Response:
        video_config = self.get_object()

        if hasattr(video_config, 'video'):
            return Response(
                {"error": "Video already exists for this config"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer: VideoSerializer = VideoSerializer(
            data={'video_file': request.FILES.get('video_file')},
            context={'request': request}
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        video = serializer.save(profile=video_config)

        process_video.delay(video.id)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def delete_video(self, request:Request, uuid:None|str=None) -> Response:
        video_config = self.get_object()

        if not hasattr(video_config, 'video'):
            return Response(
                {"error": "Video does not exists for this config"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        video_config.video.delete()
        
        video_config.refresh_from_db()
        serializer = self.get_serializer(instance=video_config)
        return Response(serializer.data, status=status.HTTP_200_OK)