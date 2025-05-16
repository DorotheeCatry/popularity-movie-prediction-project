# This makes the allocine_scraper a proper Python package
from .spiders.newreleases_spider import NewReleaseMovieSpider

__all__ = ['NewReleaseMovieSpider']