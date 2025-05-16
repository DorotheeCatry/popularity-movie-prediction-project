# This makes the allocine_scraper a proper Python package
from .spiders.newreleases_spider import NewReleaseMovieSpider
from .items import AllocineScraperParsingItem, MovieReleaseScraperParsingItem, MovieSuccessScraperItem
from .pipelines import ReleaseDatabasePipeline

__all__ = [
    'NewReleaseMovieSpider',
    'AllocineScraperParsingItem',
    'MovieReleaseScraperParsingItem',
    'MovieSuccessScraperItem',
    'ReleaseDatabasePipeline'
]