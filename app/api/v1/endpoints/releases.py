from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from app.core.security import get_current_user
from sqlmodel import Session
from app.models.users import User
from app.models.releases import Movie
import lightgbm
import pandas as pd
import joblib
from app.core.jwt_handler import verify_token

router = APIRouter()

# Load the pre-trained model with joblib
model = joblib.load("app/utils/boxoffice_model.joblib")

request_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/releases/predict")

@router.post("/releases/predict")
def predict_movie_success(
    movies_data: list,  # The movie data to process for prediction.
    token: str = Depends(request_scheme),  # Token used to authenticate the user.
      # Database session to interact with the DB.
):
    """
    Submits movie data, predicts the movie's box office success (in France and the US),
    and saves the results in the database.

    Parameters:
    - `movie_data` (Movie): Data related to the movie, such as title, duration, genre, etc.
    - `token` (str): Token used to authenticate the user making the request.
    - `session` (Session): Database session to interact with the DB.

    This function processes the movie data, predicts the movie's success using a pre-trained model, 
    and saves the results in the database.
    """
    
    # Retrieve the current user with the token
    current_user = get_current_user(token, session)

    # Prepare the movie data to pass to the prediction model.
    predictions = []

    for movie_data in movies_data:
        # Prepare the movie data to pass to the prediction model.
        movie_features = {
            "title": [movie_data.get("title")],
            "original_title": [movie_data.get("original_title")],
            "release_date": [movie_data.get("release_date")],
            "duration": [movie_data.get("duration")],
            "genres": [",".join(movie_data.get("genres", []))],
            "press_rating": [movie_data.get("press_rating")],
            "audience_rating": [movie_data.get("audience_rating")],
            "director": [",".join(movie_data.get("director", []))],
            "writer": [",".join(movie_data.get("writer", []))],
            "audience": [movie_data.get("audience")],
            "distributor": [movie_data.get("distributor")],
            "movie_type": [movie_data.get("movie_type")],
            "nationality": [",".join(movie_data.get("nationality", []))],
            "languages": [",".join(movie_data.get("languages", []))],
            "synopsis": [movie_data.get("synopsis")],
            "actors": [",".join(movie_data.get("actors", []))],
            "box_office_fr": [movie_data.get("box_office_fr")],
            "box_office_us": [movie_data.get("box_office_us")],
            "showings": [movie_data.get("showings")],
            "trailer_date": [movie_data.get("trailer_date")],
            "trailer_views": [movie_data.get("trailer_views")],
            "trailer_number": [movie_data.get("trailer_number")],
            "trailer_url": [movie_data.get("trailer_url")],
            "image_url": [movie_data.get("image_url")],
        }

        # Convert the data into a DataFrame for prediction with the model
        df_data = pd.DataFrame(movie_features)
        
        # Ensure data types are properly converted
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
        
        # Predict the movie's success
        prediction = model.predict(df_data)
        
        # Add the prediction to the list
        predictions.append(prediction[0])  # Add the first prediction (value) for each movie
    
    # Return all predictions in a readable format
    return {"predictions": predictions}




from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from pydantic import BaseModel
from datetime import datetime

from app.ml.preprocessing import prepare_features
from app.ml.embeddings import generate_embeddings

router = APIRouter()

# Load the model
MODEL_PATH = Path("models/boxoffice_model.joblib")
if not MODEL_PATH.exists():
    raise RuntimeError("Model file not found. Please train the model first.")

model = joblib.load(MODEL_PATH)



@router.post("/predict", response_model=List[PredictionResponse])
async def predict_box_office(movies: List[MovieData]):
    """
    Predict box office performance for one or more movies.
    """
    predictions = []
    
    for movie in movies:
        # Convert movie data to DataFrame
        movie_dict = {k: [v] for k, v in movie.dict().items()}
        df = pd.DataFrame(movie_dict)
        
        # Generate embeddings
        df = generate_embeddings(df)
        
        # Prepare features
        X = prepare_features(df)
        
        # Make prediction
        pred = model.predict(X)[0]
        
        # Calculate confidence interval (simplified)
        confidence = {
            "lower": pred * 0.9,  # 10% margin
            "upper": pred * 1.1
        }
        
        predictions.append(PredictionResponse(
            movie_title=movie.title,
            predicted_box_office=float(pred),
            confidence_interval=confidence
        ))
    
    return predictions