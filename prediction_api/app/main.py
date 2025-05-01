from fastapi import FastAPI
from app.routers import predictions

app = FastAPI(
    title="Movie Box Office Prediction API",
    description="API for predicting movie box office performance using machine learning",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "predictions", "description": "Movie prediction endpoints"}
    ]
)

# Include routers
app.include_router(predictions.router, prefix="/api/v1", tags=["predictions"])