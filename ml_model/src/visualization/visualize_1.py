"""
Visualization functions for the movie box office prediction pipeline.
"""
import os
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import List, Dict, Any, Optional
import shap

def set_plot_style():
    """Set the default plot style."""
    plt.style.use('seaborn-v0_8-whitegrid')
    sns.set_palette("viridis")
    
    # Increase font sizes
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['legend.fontsize'] = 10

def plot_predictions(y_true: pd.Series, y_pred: pd.Series, output_dir: Path):
    """
    Plot predictions vs actual values.
    
    Args:
        y_true: True values
        y_pred: Predicted values
        output_dir: Directory to save the plot
    """
    set_plot_style()
    
    plt.figure(figsize=(10, 8))
    
    # Create scatter plot with transparency for dense areas
    plt.scatter(y_true, y_pred, alpha=0.5, color='#1f77b4', s=40)
    
    # Add perfect prediction line
    lims = [
        min(y_true.min(), y_pred.min()),
        max(y_true.max(), y_pred.max())
    ]
    plt.plot(lims, lims, 'k--', alpha=0.7, linewidth=1)
    
    # Add labels and title
    plt.xlabel('Actual Box Office (FR)', fontsize=14)
    plt.ylabel('Predicted Box Office (FR)', fontsize=14)
    plt.title('Predicted vs Actual Box Office Results', fontsize=16)
    
    # Add grid
    plt.grid(True, alpha=0.3)
    
    # Add annotations
    rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
    r2 = 1 - np.sum((y_true - y_pred) ** 2) / np.sum((y_true - y_true.mean()) ** 2)
    
    plt.annotate(f'RMSE: {rmse:.2f}\nR²: {r2:.4f}', 
                 xy=(0.05, 0.95), xycoords='axes fraction',
                 bbox=dict(boxstyle="round,pad=0.5", fc="white", ec="gray", alpha=0.8))
    
    # Save the plot
    output_dir.mkdir(parents=True, exist_ok=True)
    plt_path = output_dir / 'predictions_vs_actual.png'
    plt.tight_layout()
    plt.savefig(plt_path, dpi=300)
    plt.close()
    
    logging.info(f"Predictions plot saved to {plt_path}")

def plot_feature_importance(model, output_dir: Path, top_n: int = 30):
    """
    Plot feature importance.
    
    Args:
        model: Trained model
        output_dir: Directory to save the plot
        top_n: Number of top features to display
    """
    set_plot_style()
    
    # Check if we have feature names
    if hasattr(model, 'feature_name_'):
        feature_names = model.feature_name_
    else:
        feature_names = [f"feature_{i}" for i in range(len(model.feature_importances_))]
    
    # Create DataFrame with importances
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False).head(top_n)
    
    # Plot
    plt.figure(figsize=(12, 10))
    sns.barplot(data=importance_df, x='importance', y='feature', palette='viridis')
    
    plt.title(f'Top {top_n} Feature Importances', fontsize=16)
    plt.xlabel('Importance', fontsize=14)
    plt.ylabel('Feature', fontsize=14)
    
    # Save the plot
    output_dir.mkdir(parents=True, exist_ok=True)
    plt_path = output_dir / 'feature_importance.png'
    plt.tight_layout()
    plt.savefig(plt_path, dpi=300)
    plt.close()
    
    logging.info(f"Feature importance plot saved to {plt_path}")

def plot_shap_summary(model, X_sample, output_dir: Path, max_display: int = 20):
    """
    Create and save SHAP summary plot.
    
    Args:
        model: Trained model
        X_sample: Sample of features to compute SHAP values
        output_dir: Directory to save the plot
        max_display: Maximum number of features to show
    """
    try:
        set_plot_style()
        
        # Create explainer
        explainer = shap.TreeExplainer(model)
        
        # Calculate SHAP values
        shap_values = explainer.shap_values(X_sample, check_additivity=False)
        
        # Create and save plot
        plt.figure(figsize=(12, 10))
        shap.summary_plot(
            shap_values, 
            X_sample,
            feature_names=X_sample.columns,
            max_display=max_display,
            show=False
        )
        
        # Save the plot
        output_dir.mkdir(parents=True, exist_ok=True)
        plt_path = output_dir / 'shap_summary.png'
        plt.tight_layout()
        plt.savefig(plt_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logging.info(f"SHAP summary plot saved to {plt_path}")
        
    except Exception as e:
        logging.error(f"Failed to create SHAP plot: {e}")

def plot_embeddings_pca_variance(pca, output_dir: Path, title: str = "PCA Explained Variance"):
    """
    Plot explained variance from PCA.
    
    Args:
        pca: Fitted PCA model
        output_dir: Directory to save the plot
        title: Plot title
    """
    set_plot_style()
    
    plt.figure(figsize=(10, 6))
    
    # Calculate cumulative explained variance
    cum_var_exp = np.cumsum(pca.explained_variance_ratio_)
    
    # Plot cumulative and individual variance
    plt.bar(range(len(pca.explained_variance_ratio_)), 
            pca.explained_variance_ratio_, 
            alpha=0.6, 
            color='skyblue',
            label='Individual explained variance')
    
    plt.step(range(len(cum_var_exp)), 
             cum_var_exp, 
             where='mid',
             color='red', 
             label='Cumulative explained variance')
    
    # Add labels and title
    plt.xlabel('Principal Components')
    plt.ylabel('Explained Variance Ratio')
    plt.title(title)
    plt.legend()
    
    # Add grid
    plt.grid(True, alpha=0.3)
    
    # Save the plot
    output_dir.mkdir(parents=True, exist_ok=True)
    plt_path = output_dir / 'pca_variance.png'
    plt.tight_layout()
    plt.savefig(plt_path, dpi=300)
    plt.close()
    
    logging.info(f"PCA variance plot saved to {plt_path}")