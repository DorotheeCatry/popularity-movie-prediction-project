# django_cinema_interface/__init__.py

from __future__ import absolute_import, unicode_literals

# Le chargement de l'application Celery
from .celery import app as celery_app

__all__ = ('celery_app',)
