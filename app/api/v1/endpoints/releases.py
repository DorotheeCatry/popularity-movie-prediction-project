from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import lightgbm
import pandas as pd
import joblib
from datetime import date
import os

# Define the input model
class MovieInput(BaseModel):
    title: str
    original_title: Optional[str] = None
    release_date: Optional[date] = None
    duration: Optional[str] = None
    genres: List[str] = []
    press_rating: Optional[float] = None
    audience_rating: Optional[float] = None
    director: List[str] = []
    writer: List[str] = []
    audience: Optional[str] = None
    distributor: Optional[str] = None
    movie_type: Optional[str] = None
    nationality: List[str] = []
    languages: List[str] = []
    synopsis: Optional[str] = None
    actors: List[str] = []
    box_office_fr: Optional[float] = None
    box_office_us: Optional[float] = None
    showings: Optional[int] = None
    trailer_date: Optional[date] = None
    trailer_views: Optional[int] = None
    trailer_number: Optional[int] = None
    trailer_url: Optional[str] = None
    image_url: Optional[str] = None

router = APIRouter()

# Load the pre-trained model with error handling
try:
    model_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "app", "utils", "boxoffice_model.joblib")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}")
    model = joblib.load(model_path)
except Exception as e:
    print(f"Error loading model: {str(e)}")
    model = None

@router.post("/releases/predict")
def predict_movie_success(movies_data: List[MovieInput]):
    """
    Predicts box office performance for a list of movies.
    
    Parameters:
    - movies_data: List of movies with their features
    
    Returns:
    - Dictionary containing predictions for each movie
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded properly")

    predictions = []

    for movie_data in movies_data:
        # Convert movie data to dictionary
        movie_dict = movie_data.dict()
        
        # Prepare features
        movie_features = {
            "title": [movie_dict["title"]],
            "original_title": [movie_dict["original_title"]],
            "release_date": [movie_dict["release_date"]],
            "duration": [movie_dict["duration"]],
            "genres": [",".join(movie_dict["genres"])],
            "press_rating": [movie_dict["press_rating"]],
            "audience_rating": [movie_dict["audience_rating"]],
            "director": [",".join(movie_dict["director"])],
            "writer": [",".join(movie_dict["writer"])],
            "audience": [movie_dict["audience"]],
            "distributor": [movie_dict["distributor"]],
            "movie_type": [movie_dict["movie_type"]],
            "nationality": [",".join(movie_dict["nationality"])],
            "languages": [",".join(movie_dict["languages"])],
            "synopsis": [movie_dict["synopsis"]],
            "actors": [",".join(movie_dict["actors"])],
            "box_office_fr": [movie_dict["box_office_fr"]],
            "box_office_us": [movie_dict["box_office_us"]],
            "showings": [movie_dict["showings"]],
            "trailer_date": [movie_dict["trailer_date"]],
            "trailer_views": [movie_dict["trailer_views"]],
            "trailer_number": [movie_dict["trailer_number"]],
            "trailer_url": [movie_dict["trailer_url"]],
            "image_url": [movie_dict["image_url"]]
        }

        # Create DataFrame
        df_data = pd.DataFrame(movie_features)
        
        # Convert data types
        df_data["release_date"] = pd.to_datetime(df_data["release_date"], errors='coerce')
        df_data["duration"] = df_data["duration"].astype("str")
        df_data["genres"] = df_data["genres"].astype("str")
        df_data["director"] = df_data["director"].astype("str")
        df_data["writer"] = df_data["writer"].astype("str")
        df_data["audience"] = df_data["audience"].astype("str")
        df_data["distributor"] = df_data["distributor"].astype("str")
        df_data["movie_type"] = df_data["movie_type"].astype("str")
        df_data["nationality"] = df_data["nationality"].astype("str")
        df_data["languages"] = df_data["languages"].astype("str")
        df_data["actors"] = df_data["actors"].astype("str")
        df_data["trailer_date"] = pd.to_datetime(df_data["trailer_date"], errors='coerce')
        
        try:
            # Make prediction
            prediction = model.predict(df_data)
            
            # Add to results
            predictions.append({
                "title": movie_dict["title"],
                "predicted_box_office": float(prediction[0])
            })
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error making prediction: {str(e)}")
    
    return {"predictions": predictions}