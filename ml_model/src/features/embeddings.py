"""
Embeddings generation module for movie entities.
"""
import os
import logging
import numpy as np
import pandas as pd
from typing import List, Optional, Union
from pathlib import Path
from gensim.models import Word2Vec
from sentence_transformers import SentenceTransformer

def clean_names(cell: Union[str, List, np.ndarray, None]) -> List[str]:
    """
    Clean and standardize names from various input formats.
    
    Args:
        cell: Input data which could be string, list, numpy array or None
        
    Returns:
        List[str]: Cleaned list of names
    """
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
    """
    Add a domain prefix to each value in a list.
    
    Args:
        values: List of strings
        prefix: Prefix to add to each string
        
    Returns:
        List of strings with prefixes added
    """
    if isinstance(values, list):
        return [f"{prefix}_{value}" for value in values]
    return []

def prepare_embedding_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare the data for embeddings by extracting relevant entities.
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with extracted entity lists
    """
    logging.info("Preparing data for embeddings")
    
    df = df.copy()
    
    # Extract entity lists
    df['actor_list'] = df['actors'].apply(clean_names)
    df['director_list'] = df['director'].apply(clean_names)
    df['writer_list'] = df['writer'].apply(clean_names)
    df['distributor_list'] = df['distributor'].apply(lambda x: x.split(',') if isinstance(x, str) else [])
    df['genre_list'] = df['genres'].apply(clean_names)
    df['nationality_list'] = df['nationality'].apply(clean_names)
    df['language_list'] = df['languages'].apply(clean_names)
    
    # Create prefixed versions for embeddings
    df['actors_prefixed'] = df['actor_list'].apply(lambda x: add_prefix(x, 'actor'))
    df['directors_prefixed'] = df['director_list'].apply(lambda x: add_prefix(x, 'director'))
    df['writers_prefixed'] = df['writer_list'].apply(lambda x: add_prefix(x, 'writer'))
    df['distributors_prefixed'] = df['distributor_list'].apply(lambda x: add_prefix(x, 'distributor'))
    df['genres_prefixed'] = df['genre_list'].apply(lambda x: add_prefix(x, 'genre'))
    df['nationalities_prefixed'] = df['nationality_list'].apply(lambda x: add_prefix(x, 'nationality'))
    df['languages_prefixed'] = df['language_list'].apply(lambda x: add_prefix(x, 'language'))
    
    # Create combined sentences for embeddings
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

def train_word2vec_model(
    sentences: List[List[str]], 
    model_name: str,
    model_dir: Path,
    vector_size: int = 300,
    window: int = 5,
    min_count: int = 2,
    sg: int = 1,
    epochs: int = 30
) -> Word2Vec:
    """
    Train a Word2Vec model on the given sentences.
    
    Args:
        sentences: List of tokenized sentences
        model_name: Name for saving the model
        model_dir: Directory to save the model
        vector_size: Dimensionality of embeddings
        window: Context window size
        min_count: Minimum word count
        sg: Training algorithm (1 for skip-gram, 0 for CBOW)
        epochs: Number of training epochs
        
    Returns:
        Trained Word2Vec model
    """
    logging.info(f"Training Word2Vec model: {model_name}")
    
    model = Word2Vec(
        sentences,
        vector_size=vector_size,
        window=window,
        min_count=min_count,
        workers=4,
        sg=sg
    )
    
    model.train(sentences, total_examples=model.corpus_count, epochs=epochs)
    
    # Save the model
    os.makedirs(model_dir, exist_ok=True)
    model_path = model_dir / f"{model_name}.model"
    model.save(str(model_path))
    logging.info(f"Model saved to {model_path}")
    
    return model

def load_or_train_word2vec(
    sentences: List[List[str]],
    model_name: str,
    model_dir: Path,
    **kwargs
) -> Word2Vec:
    """
    Load a Word2Vec model if it exists, or train a new one.
    
    Args:
        sentences: List of tokenized sentences
        model_name: Name of the model
        model_dir: Directory where models are stored
        kwargs: Additional parameters for Word2Vec training
        
    Returns:
        Word2Vec model
    """
    model_path = model_dir / f"{model_name}.model"
    
    if model_path.exists():
        logging.info(f"Loading existing Word2Vec model: {model_path}")
        return Word2Vec.load(str(model_path))
    else:
        logging.info(f"Training new Word2Vec model: {model_name}")
        return train_word2vec_model(sentences, model_name, model_dir, **kwargs)

def create_synopsis_embeddings(
    df: pd.DataFrame, 
    model_dir: Path,
    model_name: str = "sentence-transformer"
) -> np.ndarray:
    """
    Create embeddings for movie synopses using a sentence transformer.
    
    Args:
        df: DataFrame with synopsis column
        model_dir: Directory to save/load the model
        model_name: Name of the model to use
        
    Returns:
        Array of synopsis embeddings
    """
    logging.info("Creating synopsis embeddings")
    
    model_path = model_dir / model_name
    vectors_path = model_dir / "synopsis_vectors.npy"
    
    # If vectors already exist, load them
    if vectors_path.exists():
        logging.info(f"Loading existing synopsis vectors from {vectors_path}")
        return np.load(str(vectors_path))
    
    # Try to load the model or use a pre-trained one
    try:
        if model_path.exists():
            logging.info(f"Loading sentence transformer from {model_path}")
            model = SentenceTransformer(str(model_path))
        else:
            logging.info("Using pre-trained sentence transformer")
            model = SentenceTransformer('distiluse-base-multilingual-cased-v1')
            # Save the model for future use
            os.makedirs(model_path, exist_ok=True)
            model.save(str(model_path))
    except Exception as e:
        logging.error(f"Error loading sentence transformer: {e}")
        logging.info("Falling back to default model")
        model = SentenceTransformer('distiluse-base-multilingual-cased-v1')
    
    # Generate embeddings
    synopses = df['synopsis'].fillna('').tolist()
    vectors = model.encode(synopses, show_progress_bar=True)
    
    # Save the vectors
    os.makedirs(model_dir, exist_ok=True)
    np.save(str(vectors_path), vectors)
    logging.info(f"Synopsis vectors saved to {vectors_path}")
    
    return vectors

def generate_embeddings(df: pd.DataFrame, model_dir: Path) -> pd.DataFrame:
    """
    Generate all embeddings needed for the model.
    
    Args:
        df: Input DataFrame
        model_dir: Directory to save/load models
        
    Returns:
        DataFrame with added embedding features
    """
    logging.info("Generating all embeddings")
    model_dir = Path(model_dir)
    
    # Prepare data
    df = prepare_embedding_data(df)
    
    # Create sentences for different models
    sentences_actors = df['actors_prefixed'].tolist()
    sentences_cast = (
        df['actors_prefixed'].tolist() + 
        df['directors_prefixed'].tolist()
    )
    sentences_ml = df['sentence_ml'].tolist()
    
    # Train or load Word2Vec models
    model_actors = load_or_train_word2vec(
        sentences_actors, 
        "word2vec_actors",
        model_dir,
        vector_size=500,
        window=5
    )
    
    model_cast = load_or_train_word2vec(
        sentences_cast, 
        "word2vec_cast",
        model_dir,
        vector_size=500,
        window=10
    )
    
    model_sentences = load_or_train_word2vec(
        sentences_ml, 
        "word2vec_sentences",
        model_dir,
        vector_size=700,
        window=5
    )
    
    # Generate synopsis embeddings
    synopsis_vectors = create_synopsis_embeddings(df, model_dir)
    df['synopsis_vector'] = synopsis_vectors.tolist()
    
    logging.info("Embedding generation completed")
    return df