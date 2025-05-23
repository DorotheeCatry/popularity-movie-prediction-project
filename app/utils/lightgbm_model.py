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
import networkx as nx

class MovieBoxOfficePipeline:
    def __init__(self):
        self.label_encoders = {}
        self.tfidf_vectorizers = {}
        self.model = None
        self.actor_graph = None
        self.actor_director_graph = None
        
    def _create_copresence_graphs(self, actors_data, actor_director_data):
        """Create graphs for actor-actor and actor-director relationships"""
        # Actor copresence graph
        self.actor_graph = nx.Graph()
        for _, row in actors_data.iterrows():
            actor1, actor2, weight = row['actor1'], row['actor2'], row['copresence_count']
            self.actor_graph.add_edge(actor1, actor2, weight=weight)
            
        # Actor-Director graph
        self.actor_director_graph = nx.Graph()
        for _, row in actor_director_data.iterrows():
            actor, director, weight = row['actor'], row['director'], row['collaboration_count']
            self.actor_director_graph.add_edge(actor, director, weight=weight)
    
    def _calculate_actor_centrality(self, actors):
        """Calculate centrality metrics for actors"""
        if isinstance(actors, str):
            actors = actors.split(',')
        
        if not self.actor_graph:
            return {
                'avg_degree': 0,
                'avg_betweenness': 0,
                'avg_eigenvector': 0
            }
            
        metrics = {
            'avg_degree': 0,
            'avg_betweenness': 0,
            'avg_eigenvector': 0
        }
        
        valid_actors = [a for a in actors if a in self.actor_graph]
        if not valid_actors:
            return metrics
            
        degree_cent = nx.degree_centrality(self.actor_graph)
        between_cent = nx.betweenness_centrality(self.actor_graph)
        eigen_cent = nx.eigenvector_centrality(self.actor_graph, max_iter=1000)
        
        metrics['avg_degree'] = np.mean([degree_cent.get(a, 0) for a in valid_actors])
        metrics['avg_betweenness'] = np.mean([between_cent.get(a, 0) for a in valid_actors])
        metrics['avg_eigenvector'] = np.mean([eigen_cent.get(a, 0) for a in valid_actors])
        
        return metrics
    
    def _calculate_actor_director_strength(self, actors, directors):
        """Calculate collaboration strength between actors and directors"""
        if isinstance(actors, str):
            actors = actors.split(',')
        if isinstance(directors, str):
            directors = directors.split(',')
            
        if not self.actor_director_graph:
            return 0
            
        total_strength = 0
        count = 0
        
        for actor in actors:
            for director in directors:
                if self.actor_director_graph.has_edge(actor, director):
                    total_strength += self.actor_director_graph[actor][director]['weight']
                    count += 1
                    
        return total_strength / count if count > 0 else 0
    
    def _preprocess_date(self, df, column):
        df[f'{column}_year'] = pd.to_datetime(df[column]).dt.year
        df[f'{column}_month'] = pd.to_datetime(df[column]).dt.month
        df[f'{column}_day'] = pd.to_datetime(df[column]).dt.day
        df[f'{column}_day_of_week'] = pd.to_datetime(df[column]).dt.dayofweek
        return df
    
    def _process_list_features(self, df, column):
        if df[column].dtype == 'object':
            df[column] = df[column].fillna('')
            df[column] = df[column].apply(lambda x: ','.join(x) if isinstance(x, list) else x)
            # Create count feature
            df[f'{column}_count'] = df[column].str.count(',') + 1
            # Create TFIDF features
            if column not in self.tfidf_vectorizers:
                self.tfidf_vectorizers[column] = TfidfVectorizer(max_features=10)
                tfidf_matrix = self.tfidf_vectorizers[column].fit_transform(df[column])
            else:
                tfidf_matrix = self.tfidf_vectorizers[column].transform(df[column])
            
            tfidf_df = pd.DataFrame(
                tfidf_matrix.toarray(),
                columns=[f'{column}_tfidf_{i}' for i in range(10)]
            )
            df = pd.concat([df, tfidf_df], axis=1)
        return df
    
    def _encode_categorical(self, df, column):
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
        df = df.copy()
        
        # Handle dates
        date_columns = ['release_date', 'trailer_date']
        for col in date_columns:
            if col in df.columns:
                df = self._preprocess_date(df, col)
        
        # Handle list features
        list_features = ['genres', 'director', 'writer', 'nationality', 'languages', 'actors']
        for feature in list_features:
            if feature in df.columns:
                df = self._process_list_features(df, feature)
        
        # Add network features
        if 'actors' in df.columns and 'director' in df.columns:
            # Calculate actor centrality metrics
            centrality_metrics = df['actors'].apply(self._calculate_actor_centrality)
            df['actor_avg_degree'] = centrality_metrics.apply(lambda x: x['avg_degree'])
            df['actor_avg_betweenness'] = centrality_metrics.apply(lambda x: x['avg_betweenness'])
            df['actor_avg_eigenvector'] = centrality_metrics.apply(lambda x: x['avg_eigenvector'])
            
            # Calculate actor-director collaboration strength
            df['actor_director_strength'] = df.apply(
                lambda x: self._calculate_actor_director_strength(x['actors'], x['director']),
                axis=1
            )
        
        # Handle categorical features
        categorical_features = ['audience', 'distributor', 'movie_type']
        for feature in categorical_features:
            if feature in df.columns:
                df = self._encode_categorical(df, feature)
        
        # Handle numerical features
        numerical_features = ['press_rating', 'audience_rating', 'box_office_us', 
                            'showings', 'trailer_views', 'trailer_number',
                            'sum_actors_fr_entries', 'sum_directors_fr_entries',
                            'avg_stars_actors', 'avg_stars_directors']
        for feature in numerical_features:
            if feature in df.columns:
                df[feature] = df[feature].fillna(0)
        
        return df
    
    def prepare_features(self, df):
        # Select features for model training
        feature_columns = [
            # Date features
            'release_date_year', 'release_date_month', 'release_date_day', 'release_date_day_of_week',
            'trailer_date_year', 'trailer_date_month', 'trailer_date_day', 'trailer_date_day_of_week',
            
            # Numerical features
            'press_rating', 'audience_rating', 'box_office_us', 'showings', 
            'trailer_views', 'trailer_number',
            'sum_actors_fr_entries', 'sum_directors_fr_entries',
            'avg_stars_actors', 'avg_stars_directors',
            
            # Network features
            'actor_avg_degree', 'actor_avg_betweenness', 'actor_avg_eigenvector',
            'actor_director_strength',
            
            # Encoded categorical features
            'audience_encoded', 'distributor_encoded', 'movie_type_encoded',
            
            # List feature counts and TF-IDF
            'genres_count', 'director_count', 'writer_count', 'nationality_count',
            'languages_count', 'actors_count'
        ]
        
        # Add TFIDF features
        for feature in ['genres', 'director', 'writer', 'nationality', 'languages', 'actors']:
            feature_columns.extend([f'{feature}_tfidf_{i}' for i in range(10)])
        
        return df[feature_columns]
    
    def train(self, X, y):
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
        return self.model.predict(X)
    
    def save_pipeline(self, filepath):
        pipeline_data = {
            'model': self.model,
            'label_encoders': self.label_encoders,
            'tfidf_vectorizers': self.tfidf_vectorizers,
            'actor_graph': self.actor_graph,
            'actor_director_graph': self.actor_director_graph
        }
        joblib.dump(pipeline_data, filepath)
    
    def load_pipeline(self, filepath):
        pipeline_data = joblib.load(filepath)
        self.model = pipeline_data['model']
        self.label_encoders = pipeline_data['label_encoders']
        self.tfidf_vectorizers = pipeline_data['tfidf_vectorizers']
        self.actor_graph = pipeline_data['actor_graph']
        self.actor_director_graph = pipeline_data['actor_director_graph']

def train_and_save_model(allocine_data, actor_copresence_data, actor_director_data, model_save_path):
    """
    Train the model and save it to disk
    
    Args:
        allocine_data: DataFrame containing movie data from Allocine
        actor_copresence_data: DataFrame containing actor copresence data
        actor_director_data: DataFrame containing actor-director collaboration data
        model_save_path: Path where to save the trained model
    """
    # Create and train pipeline
    pipeline = MovieBoxOfficePipeline()
    
    # Create copresence graphs
    pipeline._create_copresence_graphs(actor_copresence_data, actor_director_data)
    
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