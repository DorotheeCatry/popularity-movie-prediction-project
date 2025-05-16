from django.utils import timezone
from datetime import timedelta
import logging
import sys
import os
from pathlib import Path

# Add scraping_module to Python path
scraping_path = str(Path(__file__).resolve().parent.parent / 'scraping_module')
if scraping_path not in sys.path:
    sys.path.append(scraping_path)

from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from allocine_scraper.allocine_scraper.spiders.newreleases_spider import NewReleaseMovieSpider

logger = logging.getLogger(__name__)

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
        process = CrawlerProcess(settings)
        process.crawl(NewReleaseMovieSpider)
        process.start()
        return "Scraping completed successfully"
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")
        self.retry(exc=e)
        return f"Error during scraping: {str(e)}"