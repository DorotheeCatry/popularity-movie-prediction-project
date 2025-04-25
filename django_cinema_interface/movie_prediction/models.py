from django.db import models

class Movie(models.Model):
    title = models.TextField()
    original_title = models.TextField()
    release_date = models.DateField()
    duration = models.IntegerField()
    genres = models.JSONField()  # Utilisé pour simuler un tableau de textes
    press_rating = models.FloatField(null=True, blank=True)
    audience_rating = models.FloatField(null=True, blank=True)
    director = models.JSONField()
    writer = models.JSONField()
    audience = models.TextField()
    distributor = models.TextField()
    movie_type = models.TextField()
    nationality = models.JSONField()
    languages = models.JSONField()
    synopsis = models.TextField()
    actors = models.JSONField()
    box_office_fr = models.FloatField(null=True, blank=True)
    box_office_us = models.FloatField(null=True, blank=True)
    showings = models.FloatField(null=True, blank=True)
    trailer_date = models.TextField()
    trailer_views = models.FloatField(null=True, blank=True)
    trailer_url = models.TextField()
    image_url = models.TextField()

    def __str__(self):
        return self.title


class Actor(models.Model):
    name = models.TextField(null=False, blank=False)
    mean_entries = models.IntegerField()


class MovieActor(models.Model):
    movie_in = models.ForeignKey('Movie', on_delete=models.CASCADE)
    actor_in = models.ForeignKey('Actor', on_delete=models.CASCADE)
    mean_stars_movies = models.FloatField()
    movie_count = models.IntegerField()
    mean_entries = models.IntegerField()


class Room(models.Model):
    name = models.CharField(max_length=50, unique=True)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return self.name


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