from django.contrib import admin
<<<<<<< HEAD
from .models import Movie

admin.site.register(Movie)

# @admin.register(Director)
# class DirectorAdmin(admin.ModelAdmin):
#     list_display = ('name', 'average_grade', 'popularity')

# @admin.register(Actor)
# class ActorAdmin(admin.ModelAdmin):
#     list_display = ('name', 'average_grade', 'popularity')

# @admin.register(Genre)
# class GenreAdmin(admin.ModelAdmin):
#     list_display = ('type',)

# @admin.register(Movie)
# class MovieAdmin(admin.ModelAdmin):
#     list_display = ('title', 'year', 'release_date')
#     list_filter = ('year', 'genres')
#     search_fields = ('title',)

# @admin.register(Room)
# class RoomAdmin(admin.ModelAdmin):
#     list_display = ('name', 'capacity')

=======
from .models import Movie, WeeklyProgram, Room, DailyEntry


admin.site.register(Movie)
admin.site.register(WeeklyProgram)
admin.site.register(Room)
admin.site.register(DailyEntry)

# @admin.register(Director)
# class DirectorAdmin(admin.ModelAdmin):
#     list_display = ('name', 'average_grade', 'popularity')

# @admin.register(Actor)
# class ActorAdmin(admin.ModelAdmin):
#     list_display = ('name', 'average_grade', 'popularity')

# @admin.register(Genre)
# class GenreAdmin(admin.ModelAdmin):
#     list_display = ('type',)

# @admin.register(Movie)
# class MovieAdmin(admin.ModelAdmin):
#     list_display = ('title', 'year', 'release_date')
#     list_filter = ('year', 'genres')
#     search_fields = ('title',)

# @admin.register(Room)
# class RoomAdmin(admin.ModelAdmin):
#     list_display = ('name', 'capacity')

>>>>>>> 9e9fb0e84f5769cfb8d4a7b103d4a8ad2de35b24
# @admin.register(WeeklyProgram)
# class WeeklyProgramAdmin(admin.ModelAdmin):
#     list_display = ('week_start', 'room', 'movie')
#     list_filter = ('week_start', 'room')
#     autocomplete_fields = ('movie',)

# @admin.register(DailyEntry)
# class DailyEntryAdmin(admin.ModelAdmin):
#     list_display = ('date', 'room', 'entrances')
#     list_filter = ('date', 'room')
