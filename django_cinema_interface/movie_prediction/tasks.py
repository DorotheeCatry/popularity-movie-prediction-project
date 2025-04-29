from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging
import requests
import json

from django_cinema_interface.movie_prediction.models import Movie, FilmPrediction, Program
from django_cinema_interface.scraping_module.allocine_scraper.allocine_scraper.spiders.newreleases_spider import NewReleasesSpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

logger = logging.getLogger(__name__)

# Constants for business rules
SCREEN1_CAPACITY = 120
SCREEN2_CAPACITY = 80
TICKET_PRICE = 10  # euros
FIXED_WEEKLY_COSTS = 4900  # euros
NATIONAL_TO_LOCAL_RATIO = 2000  # dividing factor to convert national to local audience
DAYS_PER_WEEK = 7

@shared_task
def scrape_new_releases():
    """
    Task to scrape new film releases from Allocine.
    Scheduled to run every Sunday at midnight.
    Collects information about films to be released the coming Wednesday.
    
    Returns:
        bool: True if scraping completed successfully, False otherwise
    """
    logger.info("Starting scraping task for new releases")
    
    # Get the date for next Wednesday (releases day)
    today = timezone.now().date()
    days_until_wednesday = (2 - today.weekday()) % 7 + 1  # 2 is Wednesday
    next_wednesday = today + timedelta(days=days_until_wednesday)
    
    try:
        # Setup the crawler
        process = CrawlerProcess(get_project_settings())
        process.crawl(NewReleasesSpider, release_date=next_wednesday.strftime('%Y-%m-%d'))
        process.start()  # This will block until the crawling is finished
        
        # After scraping completes, process the new films
        logger.info("Scraping completed, triggering prediction for new films")
        predict_audiences_for_new_films.delay()
        
        return True
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")
        return False

@shared_task
def predict_audiences_for_new_films():
    """
    Task to call the ML API and predict audience numbers for newly scraped films.
    Called after the scraping task completes.
    
    The function:
    1. Identifies films without predictions
    2. Calls the ML API for each film
    3. Calculates local metrics based on business rules
    4. Stores predictions in the database
    
    Returns:
        bool: True if prediction process completed for at least one film, False otherwise
    """
    logger.info("Starting audience prediction for new films")
    
    # Get films that need prediction (newly scraped without prediction)
    new_films = Movie.objects.filter(prediction__isnull=True)
    
    if not new_films.exists():
        logger.info("No new films found for prediction")
        return False
    
    ml_api_url = "http://fastapi:8000/predict/"  # ML service URL
    successful_predictions = 0
    
    for film in new_films:
        try:
            # Prepare data for the ML model
            film_data = {
                "title": film.title,
                "director": film.director,
                "cast": film.main_actors,
                "genre": film.genre,
                "duration": film.duration,
                "synopsis": film.synopsis,
                "release_date": film.release_date.isoformat()
            }
            
            # Call the ML API
            response = requests.post(ml_api_url, json=film_data)
            prediction_data = response.json()
            
            # Store the prediction
            national_entries = prediction_data.get('predicted_national_entries', 0)
            
            # Calculate local metrics based on business rules
            daily_local_audience = national_entries / NATIONAL_TO_LOCAL_RATIO / DAYS_PER_WEEK
            weekly_local_audience = daily_local_audience * DAYS_PER_WEEK
            weekly_revenue = weekly_local_audience * TICKET_PRICE
            weekly_profit = weekly_revenue - FIXED_WEEKLY_COSTS
            
            # Save prediction
            FilmPrediction.objects.create(
                movie=film,
                predicted_national_entries=national_entries,
                daily_local_audience=daily_local_audience,
                weekly_local_audience=weekly_local_audience,
                weekly_revenue=weekly_revenue,
                weekly_profit=weekly_profit
            )
            
            logger.info(f"Prediction created for film: {film.title}")
            successful_predictions += 1
            
        except Exception as e:
            logger.error(f"Error predicting audience for film {film.title}: {str(e)}")
    
    # After predictions, schedule the films
    if successful_predictions > 0:
        schedule_films_for_next_wednesday.delay()
        return True
    return False

@shared_task
def schedule_films_for_next_wednesday():
    """
    Task to schedule the top two films for the next Wednesday based on predictions.
    Runs after predictions are complete.
    
    The function:
    1. Identifies films scheduled for release on the next Wednesday
    2. Ranks them by predicted national entries
    3. Allocates top film to Screen 1, second to Screen 2
    4. Creates Program entries for the allocations
    
    Note: In rare cases where daily audience estimate exceeds 120 for a film,
    both screens might show the same film (not implemented in this version).
    
    Returns:
        bool: True if scheduling completed successfully, False otherwise
    """
    logger.info("Starting film scheduling for next Wednesday")
    
    # Get date for next Wednesday
    today = timezone.now().date()
    days_until_wednesday = (2 - today.weekday()) % 7 + 1
    next_wednesday = today + timedelta(days=days_until_wednesday)
    
    # Get top films by predicted audience
    top_films = FilmPrediction.objects.filter(
        movie__release_date=next_wednesday
    ).order_by('-predicted_national_entries')[:2]
    
    if len(top_films) < 2:
        logger.warning(f"Not enough films with predictions for next Wednesday. Found: {len(top_films)}")
        if len(top_films) == 0:
            return False
    
    try:
        # Clear any existing program for next Wednesday
        Program.objects.filter(date=next_wednesday).delete()
        
        # Create program for Screen 1 (highest predicted audience)
        if len(top_films) > 0:
            Program.objects.create(
                movie=top_films[0].movie,
                date=next_wednesday,
                screen=1,
                seats_capacity=SCREEN1_CAPACITY,
                estimated_attendance=min(top_films[0].daily_local_audience, SCREEN1_CAPACITY)
            )
            logger.info(f"Scheduled {top_films[0].movie.title} for Screen 1 on {next_wednesday}")
        
        # Create program for Screen 2 (second highest predicted audience)
        if len(top_films) > 1:
            Program.objects.create(
                movie=top_films[1].movie,
                date=next_wednesday,
                screen=2,
                seats_capacity=SCREEN2_CAPACITY,
                estimated_attendance=min(top_films[1].daily_local_audience, SCREEN2_CAPACITY)
            )
            logger.info(f"Scheduled {top_films[1].movie.title} for Screen 2 on {next_wednesday}")
            
        return True
    except Exception as e:
        logger.error(f"Error scheduling films for {next_wednesday}: {str(e)}")
        return False