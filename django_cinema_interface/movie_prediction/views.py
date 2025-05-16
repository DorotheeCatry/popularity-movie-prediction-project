from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, ExpressionWrapper, FloatField, Avg, Count
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Movie, WeeklyProgram, DailyEntry, Room, Actor, MovieActor
from .forms import ProgramForm, DailyEntryForm
from .tasks import scrape_new_releases


class MovieListView(LoginRequiredMixin, generic.ListView):
    model = Movie
    template_name = 'movie_prediction/movie_list.html'
    context_object_name = 'movies'
    paginate_by = 12

    def get_queryset(self):
        queryset = Movie.objects.all().order_by('-release_date')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)
        return queryset

    def get_queryset(self):
        # Récupérer les 10 films les mieux classés par box_office_fr
        return Movie.objects.order_by('-box_office_fr')[:10]


class MovieDetailView(LoginRequiredMixin, generic.DetailView):
    model = Movie
    template_name = 'movie_prediction/movie_detail.html'
    context_object_name = 'movie'

<<<<<<< HEAD
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movie = self.get_object()
        context['actors'] = MovieActor.objects.filter(movie_in=movie).select_related('actor_in')
        return context
=======
>>>>>>> 9e9fb0e84f5769cfb8d4a7b103d4a8ad2de35b24

class ProgramListView(LoginRequiredMixin, generic.ListView):
    model = WeeklyProgram
    template_name = 'movie_prediction/program_list.html'
    context_object_name = 'programs'

<<<<<<< HEAD
    def get_queryset(self):
        return WeeklyProgram.objects.select_related('room', 'movie').order_by('-week_start', 'room')
=======
>>>>>>> 9e9fb0e84f5769cfb8d4a7b103d4a8ad2de35b24

class ProgramCreateView(LoginRequiredMixin, generic.CreateView):
    model = WeeklyProgram
    form_class = ProgramForm
    template_name = 'movie_prediction/program_form.html'
    success_url = reverse_lazy('movie_prediction:program_list')

<<<<<<< HEAD
    def form_valid(self, form):
        messages.success(self.request, 'Programme ajouté avec succès.')
        return super().form_valid(form)
=======
>>>>>>> 9e9fb0e84f5769cfb8d4a7b103d4a8ad2de35b24

class DailyEntryCreateView(LoginRequiredMixin, generic.CreateView):
    model = DailyEntry
    form_class = DailyEntryForm
    template_name = 'movie_prediction/entry_form.html'
    success_url = reverse_lazy('movie_prediction:entry_list')

<<<<<<< HEAD
    def form_valid(self, form):
        messages.success(self.request, 'Entrées enregistrées avec succès.')
        return super().form_valid(form)
=======
>>>>>>> 9e9fb0e84f5769cfb8d4a7b103d4a8ad2de35b24

class DailyEntryListView(LoginRequiredMixin, generic.ListView):
    model = DailyEntry
    template_name = 'movie_prediction/entry_list.html'
    context_object_name = 'entries'

    def get_queryset(self):
        return (DailyEntry.objects
                .select_related('room')
                .order_by('-date', 'room__name'))


@login_required
def assign_best_films(request):
    today = timezone.now().date()
    next_wednesday = today + timedelta(days=(2 - today.weekday() + 7) % 7)
    
    # Get upcoming movies with predictions
    upcoming_movies = Movie.objects.filter(
        release_date__gte=next_wednesday,
        box_office_fr_pred__isnull=False
    ).order_by('-box_office_fr_pred')[:2]

    if len(upcoming_movies) < 2:
        messages.warning(request, 'Pas assez de films avec des prédictions disponibles.')
        return redirect('movie_prediction:program_list')

    # Get rooms
    room1 = Room.objects.filter(name='Salle 1').first()
    room2 = Room.objects.filter(name='Salle 2').first()

    if not (room1 and room2):
        messages.error(request, 'Configuration des salles incorrecte.')
        return redirect('movie_prediction:program_list')

    # Create or update programs
    WeeklyProgram.objects.update_or_create(
        week_start=next_wednesday,
        room=room1,
        defaults={'movie': upcoming_movies[0]}
    )
    WeeklyProgram.objects.update_or_create(
        week_start=next_wednesday,
        room=room2,
        defaults={'movie': upcoming_movies[1]}
    )

    messages.success(request, 'Programme automatique créé avec succès.')
    return redirect('movie_prediction:program_list')

@login_required
def trigger_scraping(request):
    task = scrape_new_releases.delay()
    messages.success(request, "La mise à jour des films a été lancée.")
    return redirect('movie_prediction:movie_list')