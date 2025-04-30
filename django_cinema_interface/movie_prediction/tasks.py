from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging
import requests
import json
from scrapy.utils.project import get_project_settings
from movie_prediction.models import Movie
from scraping_module.allocine_scraper.allocine_scraper.spiders.newreleases_spider import NewReleaseMovieSpider
from scrapy.crawler import CrawlerProcess

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
    Task to run the Allocine scraper and save results to the database.
    Returns the number of movies processed.
    """
    try:
        settings = get_project_settings()
        process = CrawlerProcess(settings)
        process.crawl(NewReleaseMovieSpider)
        process.start()
        return "Scraping completed successfully"
    except Exception as e:
        return f"Error during scraping: {str(e)}"