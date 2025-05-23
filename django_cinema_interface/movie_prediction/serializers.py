from rest_framework import serializers
from .models import Movie, WeeklyProgram, Room, DailyEntry

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

class WeeklyProgramSerializer(serializers.ModelSerializer):
    movie = MovieSerializer()
    room = RoomSerializer()

    class Meta:
        model = WeeklyProgram
        fields = '__all__'

class DailyEntrySerializer(serializers.ModelSerializer):
    room = RoomSerializer()
    fill_rate = serializers.SerializerMethodField()

    class Meta:
        model = DailyEntry
        fields = ['id', 'date', 'room', 'entrances', 'fill_rate']

    def get_fill_rate(self, obj):
        return (obj.entrances / obj.room.capacity) * 100 if obj.room.capacity else 0