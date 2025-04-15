"""
Utility functions for the JPBox scraper project.

This module contains helper functions used across the project, such as
loading already scraped film IDs from a CSV file.
"""

import csv

def get_scraped_film_ids(csv_path):
    """
    Reads a CSV file and retrieves a set of already scraped film IDs.

    Args:
        csv_path (str): The path to the CSV file containing scraped film data.

    Returns:
        set: A set of film IDs (as strings) that have already been scraped.

    Notes:
        - The CSV file is expected to have a column named 'film_id'.
        - If the file is not found, an empty set is returned.
    """
    scraped_ids = set()
    try:
        with open(csv_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                scraped_ids.add(row['film_id'])
    except FileNotFoundError:
        pass
    return scraped_ids
