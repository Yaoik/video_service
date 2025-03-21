from django.db import models
from common.models import Timestamped
from uploads.models import Video
import uuid
from django.core.files.storage import default_storage
from .choices import HSLStatus
import logging

logger = logging.getLogger(__name__)


class HLSVideo(Timestamped):
    video = models.ForeignKey(
            Video,
            on_delete=models.CASCADE,
            related_name="hls_videos",
    )
    uuid = models.UUIDField(
        default=uuid.uuid4, unique=True, db_index=True, editable=False
    )
    url = models.URLField(null=True)
    status = models.CharField(
        max_length=10,
        choices=HSLStatus.choices,
        default=HSLStatus.PROCESSING,
    )
    width = models.PositiveSmallIntegerField()
    height = models.PositiveSmallIntegerField()
    
    
    class Meta:
        verbose_name = "HLS_video"
        verbose_name_plural = "HLS_videos"

    def __str__(self):
        return f'<HLSVideo {self.url}>'
    
    def delete(self, *args, **kwargs) -> None:
        if self.url is not None:
            domain = default_storage.custom_domain # type: ignore
            file_path = self.url.split(domain)[-1] # Убираем http://localhost:9000/media 
            folder_path = file_path.split('index.m3u8')[0] # Убираем index.m3u8 из пути
            for file in default_storage.listdir(folder_path)[1]: # Бежим по всем файлам в dir
                if default_storage.exists(f'{folder_path}/{file}'): 
                    default_storage.delete(f'{folder_path}/{file}')

        super().delete(*args, **kwargs)