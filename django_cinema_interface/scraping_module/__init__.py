# This makes the scraping module a proper Python package
from .allocine_scraper.spiders.newreleases_spider import NewReleaseMovieSpider

__all__ = ['NewReleaseMovieSpider']