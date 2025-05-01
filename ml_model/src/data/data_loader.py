"""
Data loading module for the movie box office prediction pipeline.
"""
import os
import logging
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def load_data_from_db(table: str) -> pd.DataFrame:
    """
    Load a table from a PostgreSQL database using environment variables.
    
    Args:
        table (str): Name of the table to load.
        
    Returns:
        pd.DataFrame: Data from the table as a DataFrame.
        
    Raises:
        Exception: If database connection or query fails.
    """
    logging.info(f"Loading table '{table}' from database")
    
    try:
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_name = os.getenv("DB_NAME")
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        
        if not all([db_user, db_password, db_name]):
            raise ValueError("Missing required database environment variables")
        
        db_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        engine = create_engine(db_url, connect_args={"host": "127.0.0.1"})
        
        with engine.connect() as conn:
            df = pd.read_sql(f"SELECT * FROM {table}", conn)
            if df.columns[0].lower() in ('id', 'index', 'movie_id'):
                df.set_index(df.columns[0], inplace=True)
            
        logging.info(f"Successfully loaded {len(df)} rows from table '{table}'")
        return df
    
    except Exception as e:
        logging.error(f"Error loading table '{table}': {str(e)}")
        raise

def load_data_from_csv(file_path: str) -> pd.DataFrame:
    """
    Load data from a CSV file.
    
    Args:
        file_path (str): Path to the CSV file.
        
    Returns:
        pd.DataFrame: Data from the CSV file as a DataFrame.
        
    Raises:
        FileNotFoundError: If the file does not exist.
    """
    logging.info(f"Loading data from CSV file: {file_path}")
    
    try:
        df = pd.read_csv(file_path)
        logging.info(f"Successfully loaded {len(df)} rows from '{file_path}'")
        return df
    
    except FileNotFoundError:
        logging.error(f"CSV file not found: {file_path}")
        raise
    except Exception as e:
        logging.error(f"Error loading CSV file '{file_path}': {str(e)}")
        raise

def save_data(df: pd.DataFrame, file_path: str, index: bool = False) -> None:
    """
    Save a DataFrame to a CSV file.
    
    Args:
        df (pd.DataFrame): DataFrame to save.
        file_path (str): Path where to save the CSV.
        index (bool): Whether to include the index in the CSV.
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df.to_csv(file_path, index=index)
        logging.info(f"DataFrame saved to {file_path}")
    except Exception as e:
        logging.error(f"Error saving DataFrame to {file_path}: {str(e)}")
        raise