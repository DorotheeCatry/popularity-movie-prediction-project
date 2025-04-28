from datetime import date
from typing import Optional, List
from sqlmodel import SQLModel, Field

class MovieBase(SQLModel):
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

class Movie(MovieBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class MoviePredict(MovieBase):
    pass

class MoviePredictionResponse(SQLModel):
    title: str
    predicted_box_office_fr: float
    success_probability: float