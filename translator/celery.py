import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "translator.settings")

app = Celery("translator")
app.config_from_object('django.conf:settings', namespace="CELERY")

app.autodiscover_tasks()