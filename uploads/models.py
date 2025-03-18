from common.models import Timestamped
from django.db import models
import uuid
from users.models import User

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
        upload_to='videos/'
    )
    name = models.CharField(max_length=255)
    video_size = models.BigIntegerField()
    video_duration = models.BigIntegerField()
    
    
    def __str__(self):
        return f'<File {self.name}>'
    
    class Meta:
        verbose_name = "Видео"
        verbose_name_plural = "Видео (много)"
