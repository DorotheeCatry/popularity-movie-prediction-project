# This makes the allocine_scraper a proper Python package
from .items import AllocineScraperParsingItem, MovieReleaseScraperParsingItem, MovieSuccessScraperItem
from .middlewares import AllocineScraperSpiderMiddleware, AllocineScraperDownloaderMiddleware
from .pipelines import ReleaseDatabasePipeline
from .settings import *
from .utils import parse_date, convert_to_minutes, clean_view_count, parse_numeric, safe_int_extraction, parse_brace_string, clean_pg_array_field
from .spiders import NewReleaseMovieSpider

__all__ = [
    'AllocineScraperParsingItem',
    'MovieReleaseScraperParsingItem',
    'MovieSuccessScraperItem',
    'AllocineScraperSpiderMiddleware',
    'AllocineScraperDownloaderMiddleware',
    'ReleaseDatabasePipeline',
    'NewReleaseMovieSpider',
    'parse_date',
    'convert_to_minutes',
    'clean_view_count',
    'parse_numeric',
    'safe_int_extraction',
    'parse_brace_string',
    'clean_pg_array_field'
]