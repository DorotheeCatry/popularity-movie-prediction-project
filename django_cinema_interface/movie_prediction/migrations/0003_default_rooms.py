"""
# Add default cinema rooms

This migration creates the two default rooms required by the system:
- Salle 1 with 120 seats capacity
- Salle 2 with 80 seats capacity
"""

from django.db import migrations

def create_default_rooms(apps, schema_editor):
    Room = apps.get_model('movie_prediction', 'Room')
    Room.objects.bulk_create([
        Room(name='Salle 1', capacity=120),
        Room(name='Salle 2', capacity=80),
    ])

def remove_default_rooms(apps, schema_editor):
    Room = apps.get_model('movie_prediction', 'Room')
    Room.objects.filter(name__in=['Salle 1', 'Salle 2']).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('movie_prediction', '0002_actor_movieactor'),
    ]

    operations = [
        migrations.RunPython(create_default_rooms, remove_default_rooms),
    ]