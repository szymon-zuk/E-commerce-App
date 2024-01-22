from __future__ import absolute_import, unicode_literals
from celery import Celery
import os
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecommerceapp.settings")

celery_app = Celery(
    "ecommerceapp", broker="redis://localhost:6379", backend="redis://localhost:6379"
)

celery_app.config_from_object("django.conf:settings", namespace="CELERY")

celery_app.autodiscover_tasks(settings.INSTALLED_APPS)
