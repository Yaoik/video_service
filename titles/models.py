from django.db import models
from common.models import Timestamped
import uuid

    
class Title(Timestamped):
    uuid = models.UUIDField(
        default=uuid.uuid4, unique=True, db_index=True, editable=False
    )
    shikimori_id = models.PositiveIntegerField(unique=True, db_index=True, editable=False)
    title = models.CharField(max_length=512)
    year = models.PositiveSmallIntegerField(null=True)
    description = models.TextField(null=True)
    
    class Meta:
        verbose_name = "Тайтл"
        verbose_name_plural = "Тайтлы"

    def __str__(self) -> str:
        return f'<Title {self.uuid}>'