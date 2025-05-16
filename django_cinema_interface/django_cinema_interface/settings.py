# Add these settings to your existing settings.py
SCRAPY_SETTINGS = {
    'BOT_NAME': 'movie_scraper',
    'ROBOTSTXT_OBEY': True,
    'CONCURRENT_REQUESTS': 16,
    'DOWNLOAD_DELAY': 1,
    'COOKIES_ENABLED': False,
}