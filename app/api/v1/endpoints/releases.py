from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from app.core.security import get_current_user
from app.db.session import get_session
from sqlmodel import Session
from app.models.users import User
from app.models.releases import Movie
import lightgbm
import pandas as pd
import joblib
from app.core.jwt_handler import verify_token

router = APIRouter()

# Charger le modèle pré-entraîné avec joblib
model = joblib.load("app/utils/boxoffice_model.joblib")

request_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/releases/predict")

@router.post("/releases/predict")
def predict_movie_success(
    movie_data: Movie,  # Les données du film à traiter pour la prédiction.
    token: str = Depends(request_scheme),  # Token utilisé pour authentifier l'utilisateur.
    session: Session = Depends(get_session)  # Session de base de données pour interagir avec la BDD.
):
    """
    Soumet les données d'un film, prédit le succès du film au box-office (en France et aux États-Unis),
    et enregistre les résultats dans la base de données.

    Paramètres:
    - `movie_data` (Movie): Données liées au film, telles que le titre, la durée, le genre, etc.
    - `token` (str): Token utilisé pour authentifier l'utilisateur qui fait la demande.
    - `session` (Session): Session de base de données pour interagir avec la BDD.

    Cette fonction traite les données du film, prédit le succès du film à l'aide d'un modèle pré-entraîné, 
    et enregistre les résultats dans la base de données.
    """
    
    # Récupérer l'utilisateur actuel avec le token
    current_user = get_current_user(token, session)
    current_user_id = current_user.id  # ID de l'utilisateur pour lier la demande au bon utilisateur.

    # Préparer les données du film à passer au modèle de prédiction.
    movie_features = {
        "title": [movie_data.title],
        #"original_title": [movie_data.original_title],
        "release_date": [movie_data.release_date],
        "duration": [movie_data.duration],
        "genres": [",".join(movie_data.genres)],
        #"press_rating": [movie_data.press_rating],
        #"audience_rating": [movie_data.audience_rating],
        "director": [",".join(movie_data.director)],
        "writer": [",".join(movie_data.writer)],
        "audience": [movie_data.audience],
        "distributor": [movie_data.distributor],
        "movie_type": [movie_data.movie_type],
        "nationality": [",".join(movie_data.nationality)],
        "languages": [",".join(movie_data.languages)],
        "synopsis": [movie_data.synopsis],
        "actors": [",".join(movie_data.actors)],
        #"box_office_fr": [movie_data.box_office_fr],
        "box_office_us": [movie_data.box_office_us],
        #"showings": [movie_data.showings],
        #"trailer_date": [movie_data.trailer_date],
        #"trailer_views": [movie_data.trailer_views],
        #"trailer_number": [movie_data.trailer_number],
        #"trailer_url": [movie_data.trailer_url],
        #"image_url": [movie_data.image_url],
    }

    # Convertir les données en DataFrame pour la prédiction avec le modèle
    df_data = pd.DataFrame(movie_features)
    
    # Assurez-vous que les types de données sont correctement convertis
    df_data["release_date"] = pd.to_datetime(df_data["release_date"])
    df_data["duration"] = df_data["duration"].astype("int")
    df_data["genres"] = df_data["genres"].astype("str")
    df_data["director"] = df_data["director"].astype("str")
    df_data["writer"] = df_data["writer"].astype("str")
    df_data["audience"] = df_data["audience"].astype("str")
    df_data["distributor"] = df_data["distributor"].astype("str")
    df_data["movie_type"] = df_data["movie_type"].astype("str")
    df_data["nationality"] = df_data["nationality"].astype("str")
    df_data["languages"] = df_data["languages"].astype("str")
    df_data["actors"] = df_data["actors"].astype("str")
    #df_data["trailer_date"] = pd.to_datetime(df_data["trailer_date"], errors='coerce')
    
    # Prédire le succès du film
    prediction = model.predict(df_data)

    # Retourner la prédiction du succès du film
    return {"success": prediction}
