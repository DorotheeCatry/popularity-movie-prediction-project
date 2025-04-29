from django.db import models

class Director(models.Model):
    name = models.CharField(max_length=255)
    average_grade = models.FloatField(null=True, blank=True)
    popularity = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name

class Actor(models.Model):
    name = models.CharField(max_length=255)
    average_grade = models.FloatField(null=True, blank=True)
    popularity = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name

class Genre(models.Model):
    type = models.CharField(max_length=100)

    def __str__(self):
        return self.type



class Movie(models.Model):
    title = models.CharField(max_length=255)
    original_title = models.CharField(max_length=255, blank=True)
    release_date = models.DateField(null=True, blank=True)
    duration = models.CharField(max_length=50, blank=True)  # à transformer si possible en int
    genres = models.JSONField(default=list, blank=True)  # PostgreSQL ARRAY -> JSONField
    press_rating = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    audience_rating = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    director = models.JSONField(default=list, blank=True)  # PostgreSQL TEXT[] -> JSONField
    writer = models.JSONField(default=list, blank=True)
    audience = models.CharField(max_length=255, blank=True)
    distributor = models.CharField(max_length=255, blank=True)
    movie_type = models.CharField(max_length=100, blank=True)
    nationality = models.JSONField(default=list, blank=True)
    languages = models.JSONField(default=list, blank=True)
    synopsis = models.TextField(blank=True)
    actors = models.JSONField(default=list, blank=True)
    box_office_fr = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    box_office_us = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    showings = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    trailer_date = models.DateField(null=True, blank=True)
    trailer_views = models.BigIntegerField(null=True, blank=True)
    trailer_number = models.PositiveIntegerField(null=True, blank=True)
    trailer_url = models.URLField(blank=True)
    image_url = models.URLField(blank=True)
    box_office_fr_pred = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.title
class Movie(models.Model):
    title = models.CharField(max_length=255)
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    synopsis = models.TextField(blank=True)
    year = models.PositiveIntegerField()
    country_production = models.CharField(max_length=100)
    poster = models.URLField(blank=True)
    release_date = models.DateField()
    distributor = models.CharField(max_length=255, blank=True)

    # aggregated metrics
    average_fr_director = models.FloatField(null=True, blank=True)
    average_individual_actor = models.FloatField(null=True, blank=True)
    total_average_actors = models.FloatField(null=True, blank=True)
    sum_actors = models.FloatField(null=True, blank=True)
    sum_popularity_actors = models.FloatField(null=True, blank=True)

    # classification labels
    audience_classification = models.CharField(max_length=50, blank=True)
    languages = models.CharField(max_length=100, blank=True)

    # target
    number_entrances_fr = models.IntegerField(null=True, blank=True)

    directors = models.ManyToManyField(Director, through='DirectorInMovie')
    actors = models.ManyToManyField(Actor, through='ActorInMovie')
    genres = models.ManyToManyField(Genre, through='GenreInMovie')

    def __str__(self):
        return self.title

class DirectorInMovie(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    director = models.ForeignKey(Director, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('movie', 'director')

class ActorInMovie(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('movie', 'actor')

class GenreInMovie(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('movie', 'genre')

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
