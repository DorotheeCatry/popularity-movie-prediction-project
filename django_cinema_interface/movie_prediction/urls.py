from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api

app_name = 'movie_prediction'

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'movies', api.MovieViewSet)
router.register(r'rooms', api.RoomViewSet)
router.register(r'programs', api.WeeklyProgramViewSet, basename='program')
router.register(r'entries', api.DailyEntryViewSet, basename='entry')

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    
    # Existing view endpoints
    path('movies/', views.MovieListView.as_view(), name='movie_list'),
    path('movies/<int:pk>/', views.MovieDetailView.as_view(), name='movie_detail'),
    path('programs/', views.ProgramListView.as_view(), name='program_list'),
    path('programs/add/', views.ProgramCreateView.as_view(), name='program_add'),
    path('entries/', views.DailyEntryListView.as_view(), name='entry_list'),
    path('entries/add/', views.DailyEntryCreateView.as_view(), name='entry_add'),
    path('programs/assign_best/', views.assign_best_films, name='assign_best'),
    path('scrape/', views.trigger_scraping, name='trigger-scraping'),
]