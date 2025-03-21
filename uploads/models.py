from common.models import Timestamped
from django.db import models
import uuid
from video_configs.models import VideoConfig
from django.core.files.storage import default_storage
from django.db.models import QuerySet
from datetime import datetime
from ffmpeg import FFmpeg
import json
import logging

logger = logging.getLogger(__name__)

class Video(Timestamped):
    profile = models.OneToOneField(
        VideoConfig, 
        on_delete=models.CASCADE, 
        related_name='video',
    )
    uuid = models.UUIDField(
        default=uuid.uuid4, unique=True, db_index=True, editable=False
    )
    
    def video_upload_path(self, filename: str) -> str:
        """
        Генерирует путь для video_file с использованием даты и uuid.
        Пример: 'videos/2025/03/20/550e8400-e29b-41d4-a716-446655440000/video.mp4'
        """
        return f"videos/{datetime.now().strftime('%Y/%m/%d')}/{self.uuid}/{filename}"

    video_file = models.FileField(
        upload_to=video_upload_path,
    )
    
    # Основные метаданные
    size = models.PositiveBigIntegerField(default=0)          # Размер в байтах
    duration = models.PositiveBigIntegerField(default=0)      # Длительность в секундах
    width = models.PositiveSmallIntegerField(default=0)       # Ширина в пикселях
    height = models.PositiveSmallIntegerField(default=0)      # Высота в пикселях
    bitrate = models.PositiveIntegerField(default=0)          # Битрейт в бит/с
    
    # Дополнительные метаданные видео
    frame_rate = models.CharField(max_length=10, blank=True, null=True)  # Частота кадров, например "30/1"
    codec = models.CharField(max_length=50, blank=True, null=True)       # Кодек видео, например "h264"
    frame_count = models.PositiveBigIntegerField(blank=True, null=True)  # Количество кадров
    
    # Аудио метаданные
    audio_codec = models.CharField(max_length=50, blank=True, null=True)  # Кодек аудио, например "aac"
    sample_rate = models.PositiveIntegerField(null=True, blank=True)      # Частота дискретизации, например 44100
    channels = models.PositiveSmallIntegerField(null=True, blank=True)    # Количество каналов, например 2
    audio_bitrate = models.PositiveIntegerField(null=True, blank=True)    # Битрейт аудио, например 128000
    
    class Meta:
        verbose_name = "Video"
        verbose_name_plural = "Videos"
        
    def __str__(self):
        return f"<Video {self.profile.title}>"
    
    def delete(self, *args, **kwargs) -> None:
        logger.info(f'{self.video_file=}')
        logger.info(f'{self.video_file.name=}')
        if self.video_file and default_storage.exists(self.video_file.name):
            default_storage.delete(self.video_file.name)

        hls_videos: QuerySet = self.hls_videos # type: ignore
        for hls_video in hls_videos.all():
            hls_video.delete()

        super().delete(*args, **kwargs)