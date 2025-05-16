import requests
from datetime import date
from typing import List, Dict, Any

class MoviePredictionClient:
    def __init__(self, api_url: str = "http://localhost:8001"):
        self.api_url = api_url
        self.predict_endpoint = f"{self.api_url}/api/v1/releases/predict"

    def predict_movies(self, movies_data: List[Dict[str, Any]]) -> List[Dict[str, float]]:
        """
        Send movies data to the FastAPI service for prediction.
        
        Args:
            movies_data: List of dictionaries containing movie information
            
        Returns:
            List of predictions with movie titles and predicted box office values
        """
        try:
            response = requests.post(self.predict_endpoint, json=movies_data)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json()["predictions"]
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get prediction: {str(e)}")

# Usage example in your Django views:
"""
from django_cinema_interface.api_client import MoviePredictionClient

def predict_movie_view(request):
    client = MoviePredictionClient()
    movie_data = [{
        "title": "Example Movie",
        "release_date": "2024-03-20",
        "genres": ["Action", "Adventure"],
        "director": ["John Doe"],
        # ... other fields ...
    }]
    
    try:
        predictions = client.predict_movies(movie_data)
        return JsonResponse({"predictions": predictions})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
"""