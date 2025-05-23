import pandas as pd
import numpy as np
from lightgbm import LGBMRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from datetime import datetime
import joblib

class MovieBoxOfficePipeline:
    def __init__(self):
        self.label_encoders = {}
        self.tfidf_vectorizers = {}
        self.model = None
        
    def _preprocess_date(self, df, column):
        """Process date columns into year, month, day features"""
        df[f'{column}_year'] = pd.to_datetime(df[column]).dt.year
        df[f'{column}_month'] = pd.to_datetime(df[column]).dt.month
        df[f'{column}_day'] = pd.to_datetime(df[column]).dt.day
        return df
    
    def _process_list_features(self, df, column):
        """Process text columns into TF-IDF features"""
        if df[column].dtype == 'object':
            df[column] = df[column].fillna('')
            # Create count feature
            df[f'{column}_count'] = df[column].str.count(',') + 1
            # Create TFIDF features
            if column not in self.tfidf_vectorizers:
                self.tfidf_vectorizers[column] = TfidfVectorizer(max_features=5)
                tfidf_matrix = self.tfidf_vectorizers[column].fit_transform(df[column])
            else:
                tfidf_matrix = self.tfidf_vectorizers[column].transform(df[column])
            
            tfidf_df = pd.DataFrame(
                tfidf_matrix.toarray(),
                columns=[f'{column}_tfidf_{i}' for i in range(5)]
            )
            df = pd.concat([df, tfidf_df], axis=1)
        return df
    
    def _encode_categorical(self, df, column):
        """Encode categorical variables"""
        df[column] = df[column].fillna('unknown')
        if column not in self.label_encoders:
            self.label_encoders[column] = LabelEncoder()
            df[f'{column}_encoded'] = self.label_encoders[column].fit_transform(df[column])
        else:
            unknown_categories = ~df[column].isin(self.label_encoders[column].classes_)
            df.loc[unknown_categories, column] = 'unknown'
            df[f'{column}_encoded'] = self.label_encoders[column].transform(df[column])
        return df

    def preprocess_data(self, df):
        """Preprocess the input data"""
        df = df.copy()
        
        # Handle release_date
        if 'release_date' in df.columns:
            df = self._preprocess_date(df, 'release_date')
        
        # Handle text features
        text_features = ['genres', 'director', 'writer', 'nationality', 'languages', 'actors']
        for feature in text_features:
            if feature in df.columns:
                df = self._process_list_features(df, feature)
        
        # Handle categorical features
        categorical_features = ['distributor', 'movie_type']
        for feature in categorical_features:
            if feature in df.columns:
                df = self._encode_categorical(df, feature)
        
        # Handle numerical features
        numerical_features = [
            'press_rating', 'audience_rating', 'box_office_us',
            'sum_actors_fr_entries', 'sum_directors_fr_entries',
            'avg_stars_actors', 'avg_stars_directors'
        ]
        for feature in numerical_features:
            if feature in df.columns:
                df[feature] = df[feature].fillna(0)
        
        return df
    
    def prepare_features(self, df):
        """Prepare features for model training"""
        feature_columns = [
            # Date features
            'release_date_year', 'release_date_month', 'release_date_day',
            
            # Numerical features
            'press_rating', 'audience_rating', 'box_office_us',
            'sum_actors_fr_entries', 'sum_directors_fr_entries',
            'avg_stars_actors', 'avg_stars_directors',
            
            # Encoded categorical features
            'distributor_encoded', 'movie_type_encoded',
            
            # Text feature counts
            'genres_count', 'director_count', 'writer_count',
            'nationality_count', 'languages_count', 'actors_count'
        ]
        
        # Add TFIDF features
        for feature in ['genres', 'director', 'writer', 'nationality', 'languages', 'actors']:
            feature_columns.extend([f'{feature}_tfidf_{i}' for i in range(5)])
        
        return df[feature_columns]
    
    def train(self, X, y):
        """Train the LightGBM model"""
        self.model = LGBMRegressor(
            objective='regression',
            metric='rmse',
            num_leaves=31,
            learning_rate=0.05,
            feature_fraction=0.9,
            bagging_fraction=0.8,
            bagging_freq=5,
            verbose=-1,
            n_estimators=1000
        )
        self.model.fit(X, y)
    
    def predict(self, X):
        """Make predictions using the trained model"""
        return self.model.predict(X)
    
    def save_pipeline(self, filepath):
        """Save the pipeline to disk"""
        pipeline_data = {
            'model': self.model,
            'label_encoders': self.label_encoders,
            'tfidf_vectorizers': self.tfidf_vectorizers
        }
        joblib.dump(pipeline_data, filepath)
    
    def load_pipeline(self, filepath):
        """Load the pipeline from disk"""
        pipeline_data = joblib.load(filepath)
        self.model = pipeline_data['model']
        self.label_encoders = pipeline_data['label_encoders']
        self.tfidf_vectorizers = pipeline_data['tfidf_vectorizers']

def train_and_save_model(allocine_data, model_save_path):
    """
    Train the model and save it to disk
    
    Args:
        allocine_data: DataFrame containing movie data from Allocine
        model_save_path: Path where to save the trained model
    """
    # Create and train pipeline
    pipeline = MovieBoxOfficePipeline()
    
    # Preprocess data
    processed_df = pipeline.preprocess_data(allocine_data)
    
    # Prepare features
    X = pipeline.prepare_features(processed_df)
    y = allocine_data['box_office_fr'].fillna(0)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train model
    pipeline.train(X_train, y_train)
    
    # Evaluate model
    train_score = pipeline.model.score(X_train, y_train)
    test_score = pipeline.model.score(X_test, y_test)
    
    print(f"Train R² score: {train_score:.4f}")
    print(f"Test R² score: {test_score:.4f}")
    
    # Save pipeline
    pipeline.save_pipeline(model_save_path)
    print(f"Model saved to {model_save_path}")
    
    return pipeline