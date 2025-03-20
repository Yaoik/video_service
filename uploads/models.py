from common.models import Timestamped
from django.db import models
import uuid
from users.models import User
from .choices import VideoStatus

class Video(Timestamped):
    user = models.ForeignKey(
            User,
            on_delete=models.SET_NULL,
            null=True,
            related_name="Videos",
    )
    uuid = models.UUIDField(
        default=uuid.uuid4, unique=True, db_index=True, editable=False
    )
    video = models.FileField(
        upload_to='videos/',
        null=True,
        blank=False,
    )
    name = models.CharField(max_length=255)
    
    hls_playlist = models.URLField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=VideoStatus.choices,
        default=VideoStatus.UPLOADING
    )
    
    # Устанавливается только celery
    video_size = models.BigIntegerField(default=0)
    video_duration = models.BigIntegerField(default=0)
    
    def __str__(self):
        return f'<File {self.name}>'
    
    class Meta:
        verbose_name = "Видео"
        verbose_name_plural = "Видео (много)"
