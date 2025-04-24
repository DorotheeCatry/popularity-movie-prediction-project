from django.db import models


class Stats_director(models.Model):
    director = models.CharField(max_length=255)
    director_average_entries = models.FloatField(null=True, blank=True)
    director_med_entries = models.FloatField(null=True, blank=True)
    director_count = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.director


class Stats_actor(models.Model):
    actor = models.CharField(max_length=255)
    actor_average_entries = models.FloatField(null=True, blank=True)
    actor_med_entries = models.FloatField(null=True, blank=True)
    actor_count = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.actor


class Stats_writer(models.Model):
    writer = models.CharField(max_length=100)
    writer_avg_entries = models.FloatField(null=True, blank=True)
    writer_med_entries = models.FloatField(null=True, blank=True)
    writer_count = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.writer


class Stats_writer(models.Model):
    writer = models.CharField(max_length=100)
    writer_avg_entries = models.FloatField(null=True, blank=True)
    writer_med_entries = models.FloatField(null=True, blank=True)
    writer_count = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.writer


class Stats_distributor(models.Model):
    writer = models.CharField(max_length=100)
    writer_avg_entries = models.FloatField(null=True, blank=True)
    writer_med_entries = models.FloatField(null=True, blank=True)
    writer_count = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.writer


class Movie(models.Model):
    title = models.CharField(max_length=255)
    release_date = models.DateField()
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    genre = models.CharField(max_lengtth=255)
    
    # classification labels
    audience = models.CharField(max_length=50, blank=True)

    # nationalities of the movie
    nationality = models.CharField(max_length=50, blank=True)

    languages = models.CharField(max_length=100, blank=True)
    synopsis = models.TextField(blank=True)
    year = models.PositiveIntegerField()
    image_url = models.TextField(max_length=500, blank=True)
    box_office_fr = models.models.PositiveIntegerField(null=True, blank=True)


#     country_production = models.CharField(max_length=100)
#     poster = models.URLField(blank=True)
    
#     distributor = models.CharField(max_length=255, blank=True)

#     # aggregated metrics
#     average_fr_director = models.FloatField(null=True, blank=True)
#     average_individual_actor = models.FloatField(null=True, blank=True)
#     total_average_actors = models.FloatField(null=True, blank=True)
#     sum_actors = models.FloatField(null=True, blank=True)
#     sum_popularity_actors = models.FloatField(null=True, blank=True)


    

#     # target
#     number_entrances_fr = models.IntegerField(null=True, blank=True)

#     directors = models.ManyToManyField(Director, through='DirectorInMovie')
#     actors = models.ManyToManyField(Actor, through='ActorInMovie')
#     genres = models.ManyToManyField(Genre, through='GenreInMovie')

#     def __str__(self):
#         return self.title

# class DirectorInMovie(models.Model):
#     movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
#     director = models.ForeignKey(Director, on_delete=models.CASCADE)

#     class Meta:
#         unique_together = ('movie', 'director')

# class ActorInMovie(models.Model):
#     movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
#     actor = models.ForeignKey(Actor, on_delete=models.CASCADE)

#     class Meta:
#         unique_together = ('movie', 'actor')

# class GenreInMovie(models.Model):
#     movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
#     genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

#     class Meta:
#         unique_together = ('movie', 'genre')

# class Room(models.Model):
#     name = models.CharField(max_length=50, unique=True)
#     capacity = models.PositiveIntegerField()

#     def __str__(self):
#         return self.name

# class WeeklyProgram(models.Model):
#     week_start = models.DateField()
#     room = models.ForeignKey(Room, on_delete=models.CASCADE)
#     movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

#     class Meta:
#         unique_together = ('week_start', 'room')
#         ordering = ['-week_start', 'room']

#     def __str__(self):
#         return f"{self.week_start} - {self.room.name}: {self.movie.title}"

# class DailyEntry(models.Model):
#     date = models.DateField()
#     room = models.ForeignKey(Room, on_delete=models.CASCADE)
#     entrances = models.PositiveIntegerField()

#     class Meta:
#         unique_together = ('date', 'room')
#         ordering = ['-date', 'room']

#     def __str__(self):
#         return f"{self.date} - {self.room.name}: {self.entrances} entrées"
