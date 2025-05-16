from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from scraping_module.allocine_scraper import NewReleaseMovieSpider

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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