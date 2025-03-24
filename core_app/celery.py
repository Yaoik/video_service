import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core_app.settings")

app = Celery("core_app")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()


app.conf.beat_schedule = {
    'run-parser-queue-every-hour': {
        'task': 'titles.tasks.parser_queue',
        'schedule': 60 * 60 * 12,  # Каждые 60 минут
        'options': {'queue': 'parser_queue'},
    },
}