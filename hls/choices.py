from django.db import models


class HSLStatus(models.TextChoices):
    #UPLOADING = "uploading", "Uploading"  # Видео загружается
    PROCESSING = "processing", "Processing"  # Идет обработка (конвертация в HLS)
    READY = "ready", "Ready"  # Видео готово (HLS-список создан)
    FAILED = "failed", "Failed"  # Ошибка обработки
