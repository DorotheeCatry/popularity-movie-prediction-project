from django.db import models
from django.contrib.postgres.fields import ArrayField


class Movie(models.Model):
    title = models.TextField()
    original_title = models.CharField(max_length=255, null=True, blank=True)
    release_date = models.DateField()
    duration = models.TextField()
    genres = ArrayField(models.TextField())
    
    press_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    audience_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    
    director = ArrayField(models.TextField(), null=True, blank=True)
    writer = ArrayField(models.TextField(), null=True, blank=True)
    
    audience = models.TextField(null=True, blank=True)
    distributor = models.TextField(null=True, blank=True)
    movie_type = models.TextField(null=True, blank=True)
    
    nationality = ArrayField(models.TextField(), null=True, blank=True)
    languages = ArrayField(models.TextField(), null=True, blank=True)
    synopsis = models.TextField(null=True, blank=True)
    actors = ArrayField(models.TextField(), null=True, blank=True)
    
    box_office_fr = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    box_office_fr_pred = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    box_office_us = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    showings = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    
    trailer_date = models.DateField(null=True, blank=True)
    trailer_views = models.DecimalField(max_digits=15, decimal_places=0, null=True, blank=True)
    trailer_number = models.IntegerField(null=True, blank=True)
    
    trailer_url = models.TextField(null=True, blank=True)
    image_url = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title


class Room(models.Model):
    name = models.CharField(max_length=50, unique=True)
    capacity = models.PositiveIntegerField()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.capacity} places)"


class WeeklyProgram(models.Model):
    week_start = models.DateField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('week_start', 'room')
        ordering = ['-week_start', 'room']

    def __str__(self):
        return f"{self.week_start} - {self.room.name}: {self.movie.title}"


class DailyEntry(models.Model):
    date = models.DateField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    entrances = models.PositiveIntegerField()

    class Meta:
        unique_together = ('date', 'room')
        ordering = ['-date', 'room']

    def __str__(self):
        return f"{self.date} - {self.room.name}: {self.entrances} entrées"