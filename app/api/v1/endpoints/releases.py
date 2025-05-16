from fastapi import APIRouter
import lightgbm
import pandas as pd
import joblib

router = APIRouter()

# Load the pre-trained model with joblib
model = joblib.load("app/utils/boxoffice_model.joblib")

@router.post("/releases/predict")
def predict_movie_success(movies_data: list):
    """
    Submits movie data and predicts the movie's box office success (in France and the US).

    Parameters:
    - `movies_data` (list): List of movie data to process for prediction.

    Returns:
    - Predictions for each movie in the list.
    """
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
        predictions.append({
            "title": movie_data.get("title"),
            "predicted_box_office": float(prediction[0])
        })
    
    return {"predictions": predictions}