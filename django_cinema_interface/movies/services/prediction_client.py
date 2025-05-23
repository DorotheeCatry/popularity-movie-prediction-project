import requests
from datetime import datetime
from typing import List, Dict, Any, Optional

class PredictionClient:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.predict_endpoint = f"{self.base_url}/api/v1/releases/predict"

    def predict_movies(self, movies_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Send movie data to the prediction API and get box office predictions.
        
        Args:
            movies_data: List of movie dictionaries containing required features
            
        Returns:
            List of predictions with box office estimates and success probabilities
        """
        try:
            # Format dates properly
            for movie in movies_data:
                if movie.get('release_date'):
                    movie['release_date'] = movie['release_date'].isoformat()
                if movie.get('trailer_date'):
                    movie['trailer_date'] = movie['trailer_date'].isoformat()

            response = requests.post(self.predict_endpoint, json=movies_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get predictions: {str(e)}")