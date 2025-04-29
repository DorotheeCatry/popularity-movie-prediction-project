"""
Main script to run the movie box office prediction pipeline.
This orchestrates the entire process from data loading to model evaluation.
"""
import os
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from src.data.data_loader import load_data_from_db, load_data_from_csv
from src.features.embeddings import generate_embeddings
from src.features.feature_engineering import extract_features
from src.models.lightgbm_model import train_model, optimize_hyperparameters
from src.pipeline.pipeline import build_pipeline
from src.visualization.visualize import (
    plot_predictions, 
    plot_feature_importance,
    create_html_report,
    plot_shap_summary
)
from src.utils.utils import setup_logging, create_output_dirs

load_dotenv()

def main():
    """Main function to run the complete pipeline."""
    # Setup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    setup_logging(f"logs/run_{timestamp}.log")
    logging.info("Starting box office prediction pipeline")
    
    # Create necessary directories
    output_dir = Path("output") / timestamp
    model_dir = Path("models")
    create_output_dirs(output_dir, model_dir)
    
    try:
        # 1. Load data
        logging.info("Loading data from database")
        try:
            df_ml = load_data_from_db('allocine_ml')
            df_actors = load_data_from_db('movie_actors')
            df_directors = load_data_from_db('movie_directors')
            df_writers = load_data_from_db('movie_writers')
            df_cleaned = load_data_from_db('allocine_cleaned')
            logging.info("Data loaded successfully from database")
        except Exception as e:
            logging.warning(f"Database loading failed: {e}. Trying CSV files...")
            df_ml = load_data_from_csv('Data/allocine_ml.csv')
            logging.info("Data loaded from CSV files")
            
        # 2. Generate embeddings
        logging.info("Generating embeddings")
        df_ml = generate_embeddings(df_ml, model_dir)
        
        # 3. Feature engineering
        logging.info("Extracting features")
        df_ml = extract_features(df_ml)
        
        # 4. Build pipeline
        logging.info("Building model pipeline")
        pipeline = build_pipeline(df_ml)
        
        # 5. Train or optimize the model
        if os.getenv("OPTIMIZE_HYPERPARAMS", "False").lower() == "true":
            logging.info("Optimizing hyperparameters")
            best_params = optimize_hyperparameters(df_ml)
            logging.info(f"Best parameters: {best_params}")
            model, metrics = train_model(df_ml, pipeline, best_params)
        else:
            logging.info("Training model with default parameters")
            model, metrics = train_model(df_ml, pipeline)
        
        # 6. Plot results and generate report
        logging.info("Generating visualizations and report")
        plot_predictions(metrics["y_test"], metrics["y_pred"], output_dir)
        plot_feature_importance(model, output_dir)
        plot_shap_summary(model, metrics["X_test"].head(100), output_dir)
        
        # Create and open HTML report
        create_html_report(metrics, output_dir)
        
        # 7. Log final results
        logging.info(f"Final RMSE: {metrics['rmse']:.2f}")
        logging.info(f"Final R²: {metrics['r2']:.4f}")
        logging.info(f"Model saved to: {model_dir}/boxoffice_model.joblib")
        logging.info(f"Results available at: {output_dir}/report.html")
        
        logging.info("Pipeline completed successfully")
        
    except Exception as e:
        logging.error(f"Pipeline failed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()