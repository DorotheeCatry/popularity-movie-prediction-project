import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_cinema_interface.settings')

# Create Celery app
app = Celery('django_cinema_interface')

# Configure using Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    'scrape-new-releases': {
        'task': 'movie_prediction.tasks.scrape_new_releases',
        'schedule': crontab(hour=0, minute=0, day_of_week=3),  # Run every Wednesday at midnight
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')