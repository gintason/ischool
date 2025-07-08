import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iSchool_Ola.settings')

app = Celery('iSchool_Ola')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Look for tasks.py in all registered Django app configs
app.autodiscover_tasks()

# Use Django's database scheduler
app.conf.beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'