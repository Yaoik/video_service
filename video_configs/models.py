from django.db import models
from users.models import User
from common.models import Timestamped
import uuid



class VideoConfig(Timestamped):
    user = models.ForeignKey(
            User,
            on_delete=models.SET_NULL,
            null=True,
            related_name="videos",
    )
    uuid = models.UUIDField(
        default=uuid.uuid4, unique=True, db_index=True, editable=False
    )
    
    title = models.CharField(max_length=255)
    
    class Meta:
        verbose_name = "VideoConfig"
        verbose_name_plural = "VideoConfigs"
        
    def __str__(self) -> str:
        return f"<VideoConfig {self.title}>"
    
    def delete(self, *args, **kwargs) -> None:
        if hasattr(self, 'video'):
            self.video.delete() # type: ignore

        super().delete(*args, **kwargs)