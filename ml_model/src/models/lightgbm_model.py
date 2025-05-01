"""
LightGBM model training and optimization module.
"""
import logging
import numpy as np
import pandas as pd
from typing import Dict, Tuple, Any, List
from pathlib import Path
import joblib

import lightgbm as lgb
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import optuna
from optuna.samplers import TPESampler

def prepare_model_data(df: pd.DataFrame, target_col: str = "box_office_fr") -> Tuple[pd.DataFrame, pd.Series]:
    """
    Prepare data for model training.
    
    Args:
        df: Input DataFrame
        target_col: Target column name
        
    Returns:
        Tuple of features DataFrame and target Series
    """
    logging.info("Preparing data for model training")
    
    # List all numeric feature columns
    base_numeric_cols = [
        "duration", "year_released", "month_released", 
        "trim_released", "holidays_released", "box_office_us",
        "sum_actors_fr_entries", "sum_directors_fr_entries", "avg_stars_actors", "avg_stars_directors"
    ]
    
    # Get all PCA columns
    vector_prefixes = ["actors", "cast", "sent", "synopsis_emb"]
    vector_cols = [f"{prefix}_pca_{i}" for prefix in vector_prefixes for i in range(50)]
    
    # Combine all feature columns
    feature_cols = base_numeric_cols + vector_cols
    
    # Select features and target
    X = df[feature_cols].copy()
    y = df[target_col].copy()
    
    # Handle missing values
    X = X.fillna(0)
    
    logging.info(f"Prepared {X.shape[1]} features for modeling")
    return X, y

def split_data(X: pd.DataFrame, y: pd.Series, test_size: float = 0.2) -> Tuple:
    """
    Split data into training and testing sets.
    
    Args:
        X: Features DataFrame
        y: Target Series
        test_size: Proportion of the dataset to include in the test split
        
    Returns:
        Train-test split (X_train, X_test, y_train, y_test)
    """
    logging.info(f"Splitting data with test_size={test_size}")
    
    # Use chronological split if 'year_released' is available
    if 'year_released' in X.columns:
        logging.info("Using chronological split based on year_released")
        # Sort by year
        sorted_idx = X['year_released'].sort_values().index
        X_sorted = X.loc[sorted_idx]
        y_sorted = y.loc[sorted_idx]
        
        # Calculate split point
        split_idx = int(len(X_sorted) * (1 - test_size))
        
        X_train = X_sorted.iloc[:split_idx]
        X_test = X_sorted.iloc[split_idx:]
        y_train = y_sorted.iloc[:split_idx]
        y_test = y_sorted.iloc[split_idx:]
    else:
        # Fallback to random split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
    
    logging.info(f"Split data into {len(X_train)} training and {len(X_test)} testing samples")
    return X_train, X_test, y_train, y_test

def get_default_lightgbm_params() -> Dict[str, Any]:
    """
    Get default parameters for LightGBM model.
    
    Returns:
        Dictionary of default parameters
    """
    return {
        "objective": "regression",
        "metric": "rmse",
        "boosting_type": "gbdt",
        "learning_rate": 0.05,
        "num_leaves": 31,
        "max_depth": -1,
        "feature_fraction": 0.9,
        "bagging_fraction": 0.8,
        "bagging_freq": 5,
        "verbose": -1,
        "n_jobs": -1,
        "random_state": 42
    }

def objective(trial: optuna.Trial, X_train: pd.DataFrame, y_train: pd.Series, 
              X_valid: pd.DataFrame, y_valid: pd.Series) -> float:
    """
    Objective function for hyperparameter optimization.
    
    Args:
        trial: Optuna trial
        X_train: Training features
        y_train: Training target
        X_valid: Validation features
        y_valid: Validation target
        
    Returns:
        RMSE score
    """
    param = {
        "objective": "regression",
        "metric": "rmse",
        "boosting_type": "gbdt",
        "verbosity": -1,
        "random_state": 42,
        "n_jobs": -1,
        
        # Parameters to optimize
        "learning_rate": trial.suggest_float("learning_rate", 1e-3, 0.2, log=True),
        "n_estimators": trial.suggest_int("n_estimators", 100, 1000),
        "num_leaves": trial.suggest_int("num_leaves", 15, 100),
        "max_depth": trial.suggest_int("max_depth", 3, 12),
        "min_child_samples": trial.suggest_int("min_child_samples", 5, 100),
        "subsample": trial.suggest_float("subsample", 0.5, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
        "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
        "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 10.0, log=True),
    }

    model = lgb.LGBMRegressor(**param)
    model.fit(
        X_train, y_train,
        eval_set=[(X_valid, y_valid)],
        eval_metric="rmse",
        callbacks=[lgb.early_stopping(30)]
    )

    y_pred = model.predict(X_valid)
    rmse = mean_squared_error(y_valid, y_pred)
    return rmse

def optimize_hyperparameters(df: pd.DataFrame, n_trials: int = 50) -> Dict[str, Any]:
    """
    Optimize hyperparameters using Optuna.
    
    Args:
        df: Input DataFrame
        n_trials: Number of optimization trials
        
    Returns:
        Dictionary of best parameters
    """
    logging.info(f"Optimizing hyperparameters with {n_trials} trials")
    
    # Prepare data
    X, y = prepare_model_data(df)
    X_train, X_valid, y_train, y_valid = split_data(X, y, test_size=0.2)
    
    # Create sampler and study
    sampler = TPESampler(seed=42)
    study = optuna.create_study(direction="minimize", sampler=sampler)
    
    # Optimize
    study.optimize(
        lambda trial: objective(trial, X_train, y_train, X_valid, y_valid),
        n_trials=n_trials
    )
    
    # Log results
    logging.info(f"Best value: {study.best_value:.2f}")
    logging.info(f"Best parameters: {study.best_params}")
    
    return study.best_params

def train_model(
    df: pd.DataFrame, 
    pipeline=None, 
    params: Dict[str, Any] = None
) -> Tuple[lgb.LGBMRegressor, Dict[str, Any]]:
    """
    Train a LightGBM model.
    
    Args:
        df: Input DataFrame
        pipeline: Optional pipeline to use
        params: Model parameters (uses defaults if None)
        
    Returns:
        Tuple of trained model and metrics dictionary
    """
    logging.info("Training LightGBM model")
    
    # Prepare data
    X, y = prepare_model_data(df)
    X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.2)
    
    # Set parameters
    if params is None:
        params = get_default_lightgbm_params()
    
    # Train model
    model = lgb.LGBMRegressor(**params)
    
    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        eval_metric="rmse",
        callbacks=[lgb.early_stopping(50)])
    
    # Evaluate
    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    # Save feature importances
    feature_importances = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    # Save model
    model_path = Path("models/boxoffice_model.joblib")
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
    
    # Log metrics
    logging.info(f"RMSE: {rmse:.2f}")
    logging.info(f"MAE: {mae:.2f}")
    logging.info(f"R²: {r2:.4f}")
    logging.info(f"Model saved to {model_path}")
    
    metrics = {
        "rmse": rmse,
        "mae": mae,
        "r2": r2,
        "feature_importances": feature_importances,
        "y_test": y_test,
        "y_pred": y_pred,
        "X_test": X_test
    }
    
    return model, metrics