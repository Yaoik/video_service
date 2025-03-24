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


class VideoView(
        GenericViewSet,
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.DestroyModelMixin,
    ):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request:Request, *args, **kwargs):
        serializer:VideoSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        video:Video = serializer.save()
        
        if video.title is not None:
            video.moderated = False
            video.save(update_fields=['moderated'])
        
        process_video.delay(video.id)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)