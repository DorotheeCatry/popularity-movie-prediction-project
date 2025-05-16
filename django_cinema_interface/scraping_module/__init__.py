# This makes the scraping module a proper Python package
from .allocine_scraper import NewReleaseMovieSpider

__all__ = ['NewReleaseMovieSpider']