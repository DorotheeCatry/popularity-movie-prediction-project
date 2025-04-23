from django.contrib import admin
from .models import (
    Director, Actor, Genre, Movie,
    Room, WeeklyProgram, DailyEntry
)

@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'average_grade', 'popularity')

@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ('name', 'average_grade', 'popularity')

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('type',)

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'year', 'release_date')
    list_filter = ('year', 'genres')
    search_fields = ('title',)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity')

@admin.register(WeeklyProgram)
class WeeklyProgramAdmin(admin.ModelAdmin):
    list_display = ('week_start', 'room', 'movie')
    list_filter = ('week_start', 'room')
    autocomplete_fields = ('movie',)

@admin.register(DailyEntry)
class DailyEntryAdmin(admin.ModelAdmin):
    list_display = ('date', 'room', 'entrances')
    list_filter = ('date', 'room')
