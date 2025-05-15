from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator

class Movie(models.Model):
    title = models.TextField()
    original_title = models.TextField(null=True, blank=True)
    release_date = models.DateField()
    duration = models.IntegerField(validators=[MinValueValidator(1)])  # Store duration in minutes
    genres = ArrayField(models.TextField())
    
    press_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True,
                                     validators=[MinValueValidator(0), MaxValueValidator(5)])
    audience_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True,
                                        validators=[MinValueValidator(0), MaxValueValidator(5)])
    
    director = ArrayField(models.TextField())
    writer = ArrayField(models.TextField(), null=True, blank=True)
    
    audience = models.TextField(null=True, blank=True)
    distributor = models.TextField(null=True, blank=True)
    movie_type = models.TextField()
    
    nationality = ArrayField(models.TextField())
    languages = ArrayField(models.TextField())
    synopsis = models.TextField()
    actors = ArrayField(models.TextField())
    
    box_office_fr = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    box_office_fr_pred = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    box_office_us = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    showings = models.IntegerField(null=True, blank=True)
    
    trailer_date = models.DateField(null=True, blank=True)
    trailer_views = models.IntegerField(null=True, blank=True)
    trailer_number = models.IntegerField(null=True, blank=True)
    
    trailer_url = models.URLField(max_length=500, null=True, blank=True)
    image_url = models.URLField(max_length=500)

    class Meta:
        ordering = ['-release_date', 'title']

    def __str__(self):
        return self.title

    @property
    def formatted_duration(self):
        hours = self.duration // 60
        minutes = self.duration % 60
        return f"{hours}h{minutes:02d}"

class Actor(models.Model):
    name = models.TextField()
    mean_entries = models.IntegerField()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class MovieActor(models.Model):
    movie_in = models.ForeignKey('Movie', on_delete=models.CASCADE, related_name='movie_actors')
    actor_in = models.ForeignKey('Actor', on_delete=models.CASCADE, related_name='actor_movies')
    mean_stars_movies = models.FloatField()
    movie_count = models.IntegerField()
    mean_entries = models.IntegerField()

    class Meta:
        unique_together = ('movie_in', 'actor_in')

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

    @property
    def fill_rate(self):
        return (self.entrances / self.room.capacity) * 100 if self.room.capacity else 0