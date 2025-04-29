"""
Pipeline module for the movie box office prediction model.
"""
import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OrdinalEncoder, FunctionTransformer, StandardScaler
from sklearn.impute import SimpleImputer
import lightgbm as lgb

from src.models.lightgbm_model import get_default_lightgbm_params

class CastEmbeddingTransformer:
    """Transformer for cast embeddings."""
    
    def __init__(self, embedding_path: str):
        """
        Initialize with path to embedding model.
        
        Args:
            embedding_path: Path to the word2vec model
        """
        self.embedding_path = embedding_path
        
    def fit(self, X, y=None):
        """Fit method (no-op)."""
        return self
    
    def transform(self, X):
        """
        Transform cast strings into averaged embeddings.
        
        Args:
            X: Input array of cast strings
            
        Returns:
            Array of embeddings
        """
        # This would be implemented to load the model and compute embeddings
        # For now, it returns a dummy array
        return np.zeros((len(X), 10))

def build_pipeline(df_sample: pd.DataFrame) -> Pipeline:
    """
    Build a complete machine learning pipeline.
    
    Args:
        df_sample: Sample DataFrame to determine schema
        
    Returns:
        sklearn Pipeline
    """
    logging.info("Building model pipeline")
    
    # Define feature groups
    numeric_cols = [
        "duration", "year_released", "month_released", 
        "trim_released", "holidays_released", "box_office_us"
    ]
    
    # Add PCA columns if they exist
    vector_prefixes = ["actors", "cast", "sent", "synopsis_emb"]
    vector_cols = []
    for prefix in vector_prefixes:
        for i in range(50):
            col = f"{prefix}_pca_{i}"
            if col in df_sample.columns:
                vector_cols.append(col)
    
    # Add all numeric columns
    numeric_cols += vector_cols
    
    # Categorical columns
    categorical_cols = ["distributor", "genres", "nationality", "languages"]
    
    # Check which columns actually exist in the DataFrame
    existing_numeric_cols = [col for col in numeric_cols if col in df_sample.columns]
    existing_categorical_cols = [col for col in categorical_cols if col in df_sample.columns]
    
    # Define transformers
    numeric_transformer = Pipeline([
        ('imputer', SimpleImputer(strategy='mean')),
        ('scaler', StandardScaler())
    ])
    
    categorical_transformer = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('encoder', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1))
    ])
    
    # Define preprocessor
    transformers = []
    
    if existing_numeric_cols:
        transformers.append(('num', numeric_transformer, existing_numeric_cols))
    
    if existing_categorical_cols:
        transformers.append(('cat', categorical_transformer, existing_categorical_cols))
    
    preprocessor = ColumnTransformer(
        transformers=transformers,
        remainder='drop',
        verbose_feature_names_out=False
    )
    
    # Get default LightGBM parameters
    lgbm_params = get_default_lightgbm_params()
    
    # Create and return pipeline
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('regressor', lgb.LGBMRegressor(**lgbm_params))
    ])
    
    logging.info("Pipeline built successfully")
    return pipeline

def predict_box_office(pipeline: Pipeline, df: pd.DataFrame) -> pd.Series:
    """
    Make predictions using the trained pipeline.
    
    Args:
        pipeline: Trained pipeline
        df: Input DataFrame with features
        
    Returns:
        Series of predictions
    """
    logging.info("Making predictions")
    
    # Make predictions
    predictions = pipeline.predict(df)
    
    return pd.Series(predictions, index=df.index)