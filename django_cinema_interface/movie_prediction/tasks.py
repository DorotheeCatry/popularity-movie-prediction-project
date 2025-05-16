import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from scraping_module.allocine_scraper.spiders.newreleases_spider import NewReleaseMovieSpider

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@shared_task(
    name="scrape_new_releases",
    bind=True,
    max_retries=3,
    default_retry_delay=300
)
def scrape_new_releases(self):
    """
    Task to run the Allocine scraper and save results to the database.
    Returns the number of movies processed.
    """
    try:
        logger.info("Starting movie scraping task")
        settings = get_project_settings()
        settings.update({
            'ITEM_PIPELINES': {
                'scraping_module.allocine_scraper.pipelines.ReleaseDatabasePipeline': 300,
            },
            'SPIDER_MODULES': ['scraping_module.allocine_scraper.spiders'],
            'NEWSPIDER_MODULE': 'scraping_module.allocine_scraper.spiders',
            'LOG_LEVEL': 'DEBUG'
        })
        
        process = CrawlerProcess(settings)
        process.crawl(NewReleaseMovieSpider)
        process.start()
        
        logger.info("Scraping completed successfully")
        return "Scraping completed successfully"
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")
        self.retry(exc=e)
        return f"Error during scraping: {str(e)}"