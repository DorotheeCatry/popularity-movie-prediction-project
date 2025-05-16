from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, ExpressionWrapper, FloatField, Avg, Count
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Movie, WeeklyProgram, DailyEntry, Room
from .forms import ProgramForm, DailyEntryForm
from .tasks import scrape_new_releases


class MovieListView(LoginRequiredMixin, generic.ListView):
    model = Movie
    template_name = 'movie_prediction/movie_list.html'
    context_object_name = 'movies'
    paginate_by = 12

    def get_queryset(self):
        return Movie.objects.all().order_by('-release_date')


class MovieDetailView(LoginRequiredMixin, generic.DetailView):
    model = Movie
    template_name = 'movie_prediction/movie_detail.html'
    context_object_name = 'movie'


class ProgramListView(LoginRequiredMixin, generic.ListView):
    model = WeeklyProgram
    template_name = 'movie_prediction/program_list.html'
    context_object_name = 'programs'

    def get_queryset(self):
        return WeeklyProgram.objects.select_related('movie', 'room').order_by('-week_start')


class ProgramCreateView(LoginRequiredMixin, generic.CreateView):
    model = WeeklyProgram
    form_class = ProgramForm
    template_name = 'movie_prediction/program_form.html'
    success_url = reverse_lazy('movie_prediction:program_list')


class DailyEntryCreateView(LoginRequiredMixin, generic.CreateView):
    model = DailyEntry
    form_class = DailyEntryForm
    template_name = 'movie_prediction/entry_form.html'
    success_url = reverse_lazy('movie_prediction:entry_list')


class DailyEntryListView(LoginRequiredMixin, generic.ListView):
    model = DailyEntry
    template_name = 'movie_prediction/entry_list.html'
    context_object_name = 'entries'

    def get_queryset(self):
        queryset = DailyEntry.objects.select_related('room').order_by('-date', 'room__name')
        
        # Calculate fill rate for each entry
        for entry in queryset:
            entry.fill_rate = (entry.entrances / entry.room.capacity) * 100
            
        return queryset


@login_required
def assign_best_films(request):
    today = timezone.now().date()
    next_wednesday = today + timedelta(days=(2 - today.weekday() + 7) % 7)
    
    # Get upcoming movies with predictions
    upcoming_movies = Movie.objects.filter(
        release_date__gte=next_wednesday
    ).order_by('-box_office_fr')[:2]

    if len(upcoming_movies) < 2:
        messages.warning(request, 'Pas assez de films avec des prédictions disponibles.')
        return redirect('movie_prediction:program_list')

    # Get rooms
    rooms = Room.objects.all()[:2]
    if len(rooms) < 2:
        messages.error(request, 'Configuration des salles incorrecte.')
        return redirect('movie_prediction:program_list')

    # Create or update programs
    for room, movie in zip(rooms, upcoming_movies):
        WeeklyProgram.objects.update_or_create(
            week_start=next_wednesday,
            room=room,
            defaults={'movie': movie}
        )

    messages.success(request, 'Programme automatique créé avec succès.')
    return redirect('movie_prediction:program_list')


@login_required
def trigger_scraping(request):
    task = scrape_new_releases.delay()
    messages.success(request, "La mise à jour des films a été lancée.")
    return redirect('movie_prediction:movie_list')