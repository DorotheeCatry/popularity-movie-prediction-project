# This makes the scraping module a proper Python package
from .allocine_scraper.spiders.allocine_spider import AllocineSpider

__all__ = ['AllocineSpider']