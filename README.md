# Movie Box Office Prediction Model

A machine learning pipeline for predicting movie box office performance based on various features including cast, synopsis, and movie metadata.

## Features

- Data loading from PostgreSQL or CSV files
- Word embeddings for actors, directors, and other entities
- Synopsis text embeddings using Sentence Transformers
- Feature engineering with date extraction and dimension reduction
- LightGBM regression model with hyperparameter optimization
- SHAP-based model interpretation
- Comprehensive visualization tools

## Project Structure

```
movie-box-office-prediction/
├── logs/                    # Log files
├── models/                  # Saved models directory
├── output/                  # Output directory for plots and results
├── src/                     # Source code
│   ├── data/                # Data loading modules
│   ├── features/            # Feature engineering modules
│   ├── models/              # Model training and evaluation
│   ├── pipeline/            # Pipeline components
│   ├── utils/               # Utility functions
│   └── visualization/       # Visualization tools
├── .env                     # Environment variables (create from .env.example)
├── index.js                 # Node.js entry point
├── main.py                  # Python entry point
├── README.md                # This file
└── requirements.txt         # Python dependencies
```

## Setup

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```
   cp .env.example .env
   # Edit .env with your database credentials
   ```

## Usage

Run the full pipeline:

```
python main.py
```

This will:
1. Load data from the database or CSV files
2. Generate word embeddings for movie entities
3. Engineer features from the raw data
4. Train a LightGBM model (or optimize hyperparameters if enabled)
5. Evaluate the model and generate visualization
6. Save the trained model and results

## Model Optimization

To enable hyperparameter optimization, set `OPTIMIZE_HYPERPARAMS=True` in your `.env` file.

## Data Sources

The model uses the following data tables:
- `allocine_ml`: Main movie data
- `movie_actors`: Actor information
- `movie_directors`: Director information
- `movie_writers`: Writer information

## Output

- Trained model saved to `models/boxoffice_model.joblib`
- Prediction plots in `output/[timestamp]/predictions_vs_actual.png`
- Feature importance plots in `output/[timestamp]/feature_importance.png`
- SHAP summary in `output/[timestamp]/shap_summary.png`
- Detailed logs in `logs/run_[timestamp].log`

## License

This project is licensed under the MIT License.