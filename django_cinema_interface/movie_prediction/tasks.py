from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging
import sys
import os
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Add scraping module to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
SCRAPING_MODULE_PATH = BASE_DIR / 'scraping_module'
sys.path.append(str(SCRAPING_MODULE_PATH))

from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from scraping_module.allocine_scraper.spiders.newreleases_spider import NewReleaseMovieSpider

@shared_task(
    name="scrape_new_releases",
    bind=True,
    max_retries=3,
    default_retry_delay=300  # 5 minutes
)
def scrape_new_releases(self):
    """
    Task to run the Allocine scraper and save results to the database.
    Returns the number of movies processed.
    """
    try:
        settings = get_project_settings()
        settings.setmodule('scraping_module.allocine_scraper.settings')
        
        process = CrawlerProcess(settings)
        process.crawl(NewReleaseMovieSpider)
        process.start()
        
        return "Scraping completed successfully"
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")
        self.retry(exc=e)
        return f"Error during scraping: {str(e)}"