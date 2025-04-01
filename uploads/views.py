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
from .filters import VideoFilter
import django_filters
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
import logging
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)

class VideoView(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
):
    """Только для RD операций"""
    queryset = Video.objects.all().order_by('-id')
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = VideoFilter
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    authentication_classes = [JWTAuthentication]

class TUSDVideoVidew(APIView):
    """TUSD не позволяет раскидать хуки на разные эндпоинты, так что обрабатываются они тут"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request: Request, *args, **kwargs):
        logger.info('TUSDVideoVidew POST')
        assert isinstance(request.data, dict)
        # Определяем тип хука
        hook_type = request.data.get('Type', '').lower()
        if not hook_type:
            Response({"error": "Invalid hook type"}, status=status.HTTP_400_BAD_REQUEST)

        logger.info(f'Hook type: {hook_type}')

        if hook_type == 'pre-create':
            return self.handle_pre_create(request)
        elif hook_type == 'post-finish':
            return self.handle_post_finish(request)
        else:
            return Response({"error": "Invalid hook type"}, status=status.HTTP_400_BAD_REQUEST)

    def handle_pre_create(self, request: Request):
        """Обработка pre-create: проверка аутентификации и метаданных."""

        assert isinstance(request.data, dict)
        event:dict = request.data.get('Event', {})
        upload:dict = event.get('Upload', {})
        metadata:dict = upload.get("MetaData", "")
        if not metadata:
            return Response({"error": "Metadata required"}, status=status.HTTP_400_BAD_REQUEST)
        if not metadata.get('filetype', '').startswith('video'):
            return Response({"error": "Only Video file"}, status=status.HTTP_400_BAD_REQUEST)
        
        from datetime import datetime
        import uuid
        import json
        
        with open('json.json', 'w+', encoding='UTF-8') as f:
            f.write(json.dumps(request.data, indent=4, ensure_ascii=False))
            
        filename = metadata.get("filename", "unnamed")
        response = {
            "ChangeFileInfo": {
                "Storage":{
                    "Path": f"./videos/{datetime.now().strftime('%Y/%m/%d')}/{uuid.uuid4()}/{filename}"
                }
            }
        }
        logger.info(f"{response=}")
        return Response(response, status=status.HTTP_200_OK)

    def handle_post_finish(self, request: Request):
        """Обработка post-finish: создание объекта Video."""

        logger.info(f'{request.headers=}')
        #logger.info(f'{request.data=}')
        import json
        with open('json.json', 'w+', encoding='UTF-8') as f:
            f.write(json.dumps(request.data, indent=4, ensure_ascii=False))
        
        assert isinstance(request.data, dict)  
        event:dict = request.data.get('Event', {})
        upload:dict = event.get('Upload', {})
        storage:dict = upload.get('Storage', {})
        upload_id = upload.get("ID", None)
        upload_size = upload.get("Size", None)
        metadata:dict = upload.get("MetaData", "")

        if not upload_id or not metadata:
            return Response({"error": "Missing upload data"}, status=status.HTTP_400_BAD_REQUEST)

        filename = metadata.get("filename", None)
        if not filename:
            return Response({"error": "Filename not provided"}, status=status.HTTP_400_BAD_REQUEST)

        video_file = f"{storage.get('Path')}"

        logger.info(f'{video_file=}')

        serializer = VideoSerializer(
            data={
                'video_filename': video_file,
                'metadata': metadata,
                'size': upload_size,
                **request.data,
            },
            context={'request': request}
        )

        serializer.is_valid(raise_exception=True)
        video:Video = serializer.save()
        
        logger.info(f'Post-finish: Created video {video.uuid} for user {request.user}')
        process_video.delay(video.pk)
        
        video.refresh_from_db()
        return Response(VideoSerializer(video).data, status=status.HTTP_201_CREATED)