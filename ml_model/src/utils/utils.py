"""
Utility functions for the movie box office prediction pipeline.
"""
import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

def setup_logging(log_file: Optional[str] = None, level=logging.INFO):
    """
    Set up logging configuration.
    
    Args:
        log_file: Optional path to log file
        level: Logging level
    """
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    
    # Add file handler if specified
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        logging.info(f"Logging to {log_file}")

def create_output_dirs(*dirs):
    """
    Create output directories if they don't exist.
    
    Args:
        *dirs: Directories to create
    """
    for dir_path in dirs:
        path = Path(dir_path)
        path.mkdir(parents=True, exist_ok=True)
        logging.info(f"Created directory: {path}")

def format_number(num: float) -> str:
    """
    Format a number with commas as thousands separators.
    
    Args:
        num: Number to format
        
    Returns:
        Formatted string
    """
    return f"{int(num):,}"

def log_step(step_name: str):
    """
    Log a pipeline step with clear separation.
    
    Args:
        step_name: Name of the step
    """
    logging.info("=" * 40)
    logging.info(f" {step_name} ".center(40, "="))
    logging.info("=" * 40)

def get_formatted_metrics(metrics: Dict[str, Any]) -> str:
    """
    Format metrics for display.
    
    Args:
        metrics: Dictionary of metrics
        
    Returns:
        Formatted string of metrics
    """
    lines = ["Model Performance Metrics:"]
    
    if "rmse" in metrics:
        lines.append(f"RMSE: {metrics['rmse']:.2f}")
    
    if "mae" in metrics:
        lines.append(f"MAE: {metrics['mae']:.2f}")
    
    if "r2" in metrics:
        lines.append(f"R²: {metrics['r2']:.4f}")
    
    return "\n".join(lines)