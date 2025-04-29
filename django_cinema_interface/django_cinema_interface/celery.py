import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_cinema_interface.settings')

# Create the Celery app
app = Celery('django_cinema_interface')

# Configure Celery using settings from Django settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django app configs
app.autodiscover_tasks()

# Define periodic tasks
app.conf.beat_schedule = {
    'scrape-new-releases-sunday-midnight': {
        'task': 'movie_prediction.tasks.scrape_new_releases',
        'schedule': crontab(minute=0, hour=0, day_of_week=0),  # Sunday at midnight
        'args': (),
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')