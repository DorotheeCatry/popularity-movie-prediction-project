from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from .models import Movie
from .services.prediction_client import PredictionClient
from typing import List, Dict, Any

class MovieListView(ListView):
    model = Movie
    template_name = 'movies/movie_list.html'
    context_object_name = 'movies'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get predictions for all movies
        predictions = self.get_predictions(self.object_list)
        
        # Add predictions to context
        movies_with_predictions = []
        for movie in self.object_list:
            movie_prediction = next(
                (p for p in predictions if p['title'] == movie.title),
                {'predicted_box_office': 0, 'success_probability': 0}
            )
            movies_with_predictions.append({
                'movie': movie,
                'prediction': movie_prediction
            })
            
        context['movies_with_predictions'] = movies_with_predictions
        return context

    def get_predictions(self, movies) -> List[Dict[str, Any]]:
        """Get predictions for a list of movies"""
        try:
            client = PredictionClient()
            movies_data = [
                {
                    'title': movie.title,
                    'original_title': movie.original_title,
                    'release_date': movie.release_date,
                    'duration': movie.duration,
                    'genres': movie.genres.split(',') if movie.genres else [],
                    'press_rating': movie.press_rating,
                    'audience_rating': movie.audience_rating,
                    'director': movie.director.split(',') if movie.director else [],
                    'writer': movie.writer.split(',') if movie.writer else [],
                    'audience': movie.audience,
                    'distributor': movie.distributor,
                    'movie_type': movie.movie_type,
                    'nationality': movie.nationality.split(',') if movie.nationality else [],
                    'languages': movie.languages.split(',') if movie.languages else [],
                    'synopsis': movie.synopsis,
                    'actors': movie.actors.split(',') if movie.actors else [],
                    'box_office_fr': movie.box_office_fr,
                    'box_office_us': movie.box_office_us,
                    'showings': movie.showings,
                    'trailer_date': movie.trailer_date,
                    'trailer_views': movie.trailer_views,
                    'trailer_number': movie.trailer_number,
                    'trailer_url': movie.trailer_url,
                    'image_url': movie.image_url
                }
                for movie in movies
            ]
            return client.predict_movies(movies_data)
        except Exception as e:
            print(f"Error getting predictions: {str(e)}")
            return []

class MovieDetailView(DetailView):
    model = Movie
    template_name = 'movies/movie_detail.html'
    context_object_name = 'movie'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get prediction for single movie
        movie = self.object
        predictions = self.get_prediction(movie)
        if predictions:
            context['prediction'] = predictions[0]
        
        return context

    def get_prediction(self, movie) -> List[Dict[str, Any]]:
        """Get prediction for a single movie"""
        try:
            client = PredictionClient()
            movie_data = [{
                'title': movie.title,
                'original_title': movie.original_title,
                'release_date': movie.release_date,
                'duration': movie.duration,
                'genres': movie.genres.split(',') if movie.genres else [],
                'press_rating': movie.press_rating,
                'audience_rating': movie.audience_rating,
                'director': movie.director.split(',') if movie.director else [],
                'writer': movie.writer.split(',') if movie.writer else [],
                'audience': movie.audience,
                'distributor': movie.distributor,
                'movie_type': movie.movie_type,
                'nationality': movie.nationality.split(',') if movie.nationality else [],
                'languages': movie.languages.split(',') if movie.languages else [],
                'synopsis': movie.synopsis,
                'actors': movie.actors.split(',') if movie.actors else [],
                'box_office_fr': movie.box_office_fr,
                'box_office_us': movie.box_office_us,
                'showings': movie.showings,
                'trailer_date': movie.trailer_date,
                'trailer_views': movie.trailer_views,
                'trailer_number': movie.trailer_number,
                'trailer_url': movie.trailer_url,
                'image_url': movie.image_url
            }]
            return client.predict_movies(movie_data)
        except Exception as e:
            print(f"Error getting prediction: {str(e)}")
            return []