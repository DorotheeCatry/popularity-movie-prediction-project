# django_cinema_interface/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Le nom du module de l'application Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_cinema_interface.settings')

# Création de l'instance Celery
app = Celery('django_cinema_interface')

# Utilisation de la configuration de Celery à partir des paramètres Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Découverte automatique des tâches dans les applications Django
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
