from django.urls import path
from . import views

app_name = 'movie_prediction'

urlpatterns = [
    path('movies/', views.MovieListView.as_view(), name='movie_list'),
    path('movies/<int:pk>/', views.MovieDetailView.as_view(), name='movie_detail'),
    path('programs/', views.ProgramListView.as_view(), name='program_list'),
    path('programs/add/', views.ProgramCreateView.as_view(), name='program_add'),
    path('entries/', views.DailyEntryListView.as_view(), name='entry_list'),
    path('entries/add/', views.DailyEntryCreateView.as_view(), name='entry_add'),
    path('programs/assign_best/', views.assign_best_films, name='assign_best'),
]