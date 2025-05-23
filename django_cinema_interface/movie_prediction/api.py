from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import Movie, WeeklyProgram, Room, DailyEntry
from .serializers import MovieSerializer, WeeklyProgramSerializer, RoomSerializer, DailyEntrySerializer

class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Movie.objects.all().order_by('-release_date')
    serializer_class = MovieSerializer

class RoomViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

class WeeklyProgramViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WeeklyProgramSerializer

    def get_queryset(self):
        today = timezone.now().date()
        return WeeklyProgram.objects.filter(
            week_start__gte=today - timedelta(days=7)
        ).select_related('movie', 'room').order_by('-week_start')

    @action(detail=False)
    def current_week(self, request):
        today = timezone.now().date()
        days_since_wed = (today.weekday() - 2) % 7
        week_start = today - timedelta(days=days_since_wed)
        
        programs = WeeklyProgram.objects.filter(
            week_start=week_start
        ).select_related('movie', 'room')
        
        serializer = self.get_serializer(programs, many=True)
        return Response(serializer.data)

class DailyEntryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DailyEntrySerializer

    def get_queryset(self):
        return DailyEntry.objects.select_related('room').order_by('-date', 'room__name')