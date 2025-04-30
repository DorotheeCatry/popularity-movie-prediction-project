
# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Movie, WeeklyProgram, DailyEntry, Room
from .forms import ProgramForm, DailyEntryForm
from datetime import date, timedelta
from django.db.models import F, ExpressionWrapper, FloatField
from django.contrib import messages
from .tasks import scrape_new_releases

# from .ml import load_model, predict

def trigger_scraping(request):
    task = scrape_new_releases.delay()
    messages.success(request, "Scraping task has been initiated")
    return redirect('movie-list')


class MovieListView(LoginRequiredMixin, generic.ListView):
    model = Movie
    template_name = 'movie_prediction/movie_list.html'
    context_object_name = 'movies'

    def get_queryset(self):
        # Récupérer les 10 films les mieux classés par box_office_fr
        return Movie.objects.order_by('-box_office_fr')[:10]


class MovieDetailView(LoginRequiredMixin, generic.DetailView):
    model = Movie
    template_name = 'movie_prediction/movie_detail.html'
    context_object_name = 'movie'


class ProgramListView(LoginRequiredMixin, generic.ListView):
    model = WeeklyProgram
    template_name = 'movie_prediction/program_list.html'
    context_object_name = 'programs'


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
        return (
            DailyEntry.objects
                .select_related('room')
                .annotate(
                    fill_rate=ExpressionWrapper(
                        F('entrances') * 100.0 / F('room__capacity'),
                        output_field=FloatField(),
                    )
                )
                .order_by('-date', 'room__name')
        )


@login_required
def assign_best_films(request):
    # Determine next Wednesday
    today = date.today()
    days_ahead = (2 - today.weekday() + 7) % 7  # 2 = Wednesday
    next_wed = today + timedelta(days=days_ahead or 7)

    # Load ML model and predict for upcoming movies
    upcoming = Movie.objects.filter(release_date__gte=next_wed)
    predictions = []
    # model = load_model()
    for m in upcoming:
        # est = predict(model, m)
        est = m.number_entrances_fr or 0
        predictions.append((m, est))
    predictions.sort(key=lambda x: x[1], reverse=True)
    best = predictions[:2]

    # Assign to rooms 1 and 2
    room1 = get_object_or_404(Room, name='Salle 1')
    room2 = get_object_or_404(Room, name='Salle 2')
    if len(best) >= 1:
        WeeklyProgram.objects.update_or_create(
            week_start=next_wed, room=room1,
            defaults={'movie': best[0][0]}
        )
    if len(best) >= 2:
        WeeklyProgram.objects.update_or_create(
            week_start=next_wed, room=room2,
            defaults={'movie': best[1][0]}
        )
    return redirect('movie_prediction:program_list')