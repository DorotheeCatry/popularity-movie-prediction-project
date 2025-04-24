from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length=255)
    release_date = models.DateField()
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    genre = models.CharField(max_length=255)
    audience = models.CharField(max_length=50, blank=True)
    nationality = models.CharField(max_length=50, blank=True)
    languages = models.CharField(max_length=100, blank=True)
    synopsis = models.TextField(blank=True)
    year = models.PositiveIntegerField()
    image_url = models.TextField(blank=True)
    box_office_fr = models.PositiveIntegerField(null=True, blank=True)


class StatsDirector(models.Model):
    director = models.CharField(max_length=255)
    director_avg_entries = models.FloatField(null=True, blank=True)
    director_med_entries = models.FloatField(null=True, blank=True)
    director_count = models.IntegerField(null=True, blank=True)
    movies = models.ManyToManyField('Movie', through='DirectorInMovie')

    def __str__(self):
        return self.director


class DirectorInMovie(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    stats_director = models.ForeignKey(StatsDirector, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('movie', 'stats_director')


class StatsActor(models.Model):
    actor = models.CharField(max_length=255)
    actor_average_entries = models.FloatField(null=True, blank=True)
    actor_med_entries = models.FloatField(null=True, blank=True)
    actor_count = models.IntegerField(null=True, blank=True)
    movies = models.ManyToManyField('Movie', through='ActorInMovie')

    def __str__(self):
        return self.actor


class ActorInMovie(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    stats_actor = models.ForeignKey(StatsActor, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('movie', 'stats_actor')


class StatsWriter(models.Model):
    writer = models.CharField(max_length=100)
    writer_avg_entries = models.FloatField(null=True, blank=True)
    writer_med_entries = models.FloatField(null=True, blank=True)
    writer_count = models.IntegerField(null=True, blank=True)
    movies = models.ManyToManyField('Movie', through='WriterInMovie')

    def __str__(self):
        return self.writer


class WriterInMovie(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    stats_writer = models.ForeignKey(StatsWriter, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('movie', 'stats_writer')



class StatsDistributor(models.Model):
    distributor = models.CharField(max_length=100)
    dis_mean = models.FloatField(null=True, blank=True)
    dist_count = models.IntegerField(null=True, blank=True)
    dist_te = models.FloatField(null=True, blank=True)
    movies = models.ManyToManyField('Movie', through='DistributorInMovie')

    def __str__(self):
        return self.distributor


class DistributorInMovie(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    stats_distributor = models.ForeignKey(StatsDistributor, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('movie', 'stats_distributor')


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