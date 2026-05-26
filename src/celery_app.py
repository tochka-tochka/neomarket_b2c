import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neomarket_b2c.settings')

app = Celery('src')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()