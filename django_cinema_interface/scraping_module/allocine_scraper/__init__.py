"""
Allocine scraper module initialization
"""
from .items import MovieReleaseScraperParsingItem
from .pipelines import ReleaseDatabasePipeline

__all__ = [
    'MovieReleaseScraperParsingItem',
    'ReleaseDatabasePipeline'
]