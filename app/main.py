from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import releases

app = FastAPI(
    title="Movie Box Office Prediction API",
    description="API for predicting movie box office performance using machine learning",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "predictions", "description": "Movie prediction endpoints"}
    ]
)

# Configure CORS to allow requests from Django application
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],  # Django development server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the predictions router
app.include_router(releases.router, prefix="/api/v1", tags=["predictions"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Movie Box Office Prediction API"}