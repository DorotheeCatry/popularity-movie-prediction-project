"""
Feature engineering module for the movie box office prediction pipeline.
"""
import logging
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Callable
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA, TruncatedSVD
from gensim.models import Word2Vec

def clean_names(cell):
    """Clean and standardize names from various input formats."""
    if cell is None:
        return []
    if isinstance(cell, float) and pd.isna(cell):
        return []
    if isinstance(cell, list):
        return cell
    if isinstance(cell, np.ndarray):
        return cell.tolist()
    if isinstance(cell, str):
        return cell.replace('{', '').replace('}', '').split('|')
    return []

def add_prefix(values: List[str], prefix: str) -> List[str]:
    """Add a domain prefix to each value in a list."""
    if isinstance(values, list):
        return [f"{prefix}_{value}" for value in values]
    return []

def prepare_prefixed_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare prefixed columns for embeddings."""
    df = df.copy()
    df = df.dropna(subset=['box_office_fr'])
    
    # Extract entity lists
    df['actor_list'] = df['actors'].apply(clean_names)
    df['director_list'] = df['director'].apply(clean_names)
    df['writer_list'] = df['writer'].apply(clean_names)
    df['distributor_list'] = df['distributor'].apply(lambda x: x.split(',') if isinstance(x, str) else [])
    df['genre_list'] = df['genres'].apply(clean_names)
    df['nationality_list'] = df['nationality'].apply(clean_names)
    df['language_list'] = df['languages'].apply(clean_names)
    
    # Create prefixed versions
    df['actors_prefixed'] = df['actor_list'].apply(lambda x: add_prefix(x, 'actor'))
    df['directors_prefixed'] = df['director_list'].apply(lambda x: add_prefix(x, 'director'))
    df['writers_prefixed'] = df['writer_list'].apply(lambda x: add_prefix(x, 'writer'))
    df['distributors_prefixed'] = df['distributor_list'].apply(lambda x: add_prefix(x, 'distributor'))
    df['genres_prefixed'] = df['genre_list'].apply(lambda x: add_prefix(x, 'genre'))
    df['nationalities_prefixed'] = df['nationality_list'].apply(lambda x: add_prefix(x, 'nationality'))
    df['languages_prefixed'] = df['language_list'].apply(lambda x: add_prefix(x, 'language'))
    
    # Create combined prefixed lists
    df['cast_prefixed'] = df.apply(
        lambda row: row['actors_prefixed'] + row['directors_prefixed'],
        axis=1
    )
    
    df['sentence_ml'] = df.apply(
        lambda row: (
            row['actors_prefixed'] +
            row['directors_prefixed'] +
            row['writers_prefixed'] +
            row['distributors_prefixed'] +
            row['genres_prefixed'] +
            row['nationalities_prefixed'] +
            row['languages_prefixed']
        ),
        axis=1
    )
    
    return df

def average_vector_prefixed(names: List[str], model: Word2Vec) -> np.ndarray:
    """
    Calculate the average vector for a list of prefixed names.
    
    Args:
        names: List of names with prefixes
        model: Word2Vec model
        
    Returns:
        Average vector for the names
    """
    vecs = [model.wv[n] for n in names if n in model.wv]
    return np.mean(vecs, axis=0) if vecs else np.zeros(model.vector_size)

def is_school_holiday(date: pd.Timestamp) -> bool:
    """
    Check if a date falls during French school holidays.
    
    Args:
        date: Date to check
        
    Returns:
        True if the date is during school holidays
    """
    month = date.month
    day = date.day
    
    # Summer holidays (July-August)
    if month in {7, 8}:
        return True
    
    # Christmas holidays
    if (month == 12 and day >= 20) or (month == 1 and day <= 3):
        return True
    
    # Winter/Spring holidays (simplified)
    if (month == 2 and day >= 10) or (month == 3 and day <= 10):
        return True
    
    return False

def extract_date_features(df: pd.DataFrame, date_col: str = "release_date") -> pd.DataFrame:
    """
    Extract features from date column.
    
    Args:
        df: Input DataFrame
        date_col: Name of the date column
        
    Returns:
        DataFrame with additional date features
    """
    logging.info(f"Extracting date features from {date_col}")
    
    df = df.copy()
    
    # Ensure date column is datetime
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    
    # Extract features
    df["month_released"] = df[date_col].dt.month.astype("int8")
    df["trim_released"] = df[date_col].dt.quarter.astype("int8")
    df["year_released"] = df[date_col].dt.year.astype("int16")
    df["day_of_week"] = df[date_col].dt.dayofweek.astype("int8")
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype("int8")
    df["holidays_released"] = df[date_col].apply(is_school_holiday).astype("int8")
    
    return df

def create_embedding_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create features from embeddings.
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with embedding features
    """
    logging.info("Creating embedding features")
    
    df = df.copy()
    
    # First prepare prefixed columns
    df = prepare_prefixed_columns(df)
    
    # Load models
    try:
        model_act = Word2Vec.load("models/word2vec_actors.model")
        model_cast = Word2Vec.load("models/word2vec_cast.model")
        model_sentences = Word2Vec.load("models/word2vec_sentences.model")
        logging.info("Loaded Word2Vec models successfully")
    except Exception as e:
        logging.error(f"Failed to load Word2Vec models: {e}")
        return df
    
    # Create embedding columns
    df["actors_emb"] = df["actors_prefixed"].apply(
        lambda x: average_vector_prefixed(x, model_act)
    )
    
    df["cast_emb"] = df["cast_prefixed"].apply(
        lambda x: average_vector_prefixed(x, model_cast)
    )
    
    df["sentence_emb"] = df["sentence_ml"].apply(
        lambda x: average_vector_prefixed(x, model_sentences)
    )
    
    df["duration"] = pd.to_numeric(df["duration"], errors="coerce")

    
    return df

def reduce_embedding_dimensions(
    df: pd.DataFrame, 
    column: str, 
    prefix: str, 
    n_components: int = 50
) -> pd.DataFrame:
    """
    Reduce dimensions of embedding vectors using PCA.
    
    Args:
        df: Input DataFrame
        column: Column containing embedding vectors
        prefix: Prefix for new columns
        n_components: Number of components to keep
        
    Returns:
        DataFrame with additional PCA component columns
    """
    logging.info(f"Reducing dimensions for {column} to {n_components} components")
    
    df = df.copy()
    
    # Stack embeddings into array
    vectors = np.vstack(df[column].values)
    
    # Standardize
    vectors_scaled = StandardScaler().fit_transform(vectors)
    
    # Apply PCA
    pca = PCA(n_components=n_components, random_state=42)
    vectors_reduced = pca.fit_transform(vectors_scaled)
    
    # Add components as new columns
    for i in range(n_components):
        df[f"{prefix}_pca_{i}"] = vectors_reduced[:, i]
    
    logging.info(f"Created {n_components} PCA components for {column}")
    return df

def reduce_synopsis_dimensions(df: pd.DataFrame, n_components: int = 50) -> pd.DataFrame:
    """
    Reduce dimensions of synopsis vectors using SVD.
    
    Args:
        df: Input DataFrame
        n_components: Number of components to keep
        
    Returns:
        DataFrame with additional synopsis component columns
    """
    logging.info(f"Reducing synopsis dimensions to {n_components} components")
    
    df = df.copy()
    
    # Stack vectors
    synopsis_vectors = np.stack(df['synopsis_vector'].values)
    
    # Apply SVD (better for text than PCA)
    svd = TruncatedSVD(n_components=n_components, random_state=42)
    synopsis_reduced = svd.fit_transform(synopsis_vectors)
    
    # Add components as new columns
    for i in range(n_components):
        df[f"synopsis_emb_pca_{i}"] = synopsis_reduced[:, i]
    
    logging.info(f"Created {n_components} SVD components for synopsis")
    return df

def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract all features for the model.
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with all extracted features
    """
    logging.info("Starting feature extraction")
    
    # First create embeddings
    df = create_embedding_features(df)
    
    # Date features
    df = extract_date_features(df)
    
    # Then reduce dimensions of embeddings
    if 'actors_emb' in df.columns:
        df = reduce_embedding_dimensions(df, "actors_emb", "actors")
    if 'cast_emb' in df.columns:
        df = reduce_embedding_dimensions(df, "cast_emb", "cast")
    if 'sentence_emb' in df.columns:
        df = reduce_embedding_dimensions(df, "sentence_emb", "sent")
    if 'synopsis_vector' in df.columns:
        df = reduce_synopsis_dimensions(df)
    
    logging.info("Feature extraction complete")
    return df