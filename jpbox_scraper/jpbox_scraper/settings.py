"""
Scrapy settings for the JPBox scraper project.

This file contains the configuration settings for the Scrapy project, including
spider modules, user agent, export settings, and other middleware or extension
configurations. For more details, refer to the Scrapy documentation:

- General settings: https://docs.scrapy.org/en/latest/topics/settings.html
- Downloader middleware: https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
- Spider middleware: https://docs.scrapy.org/en/latest/topics/spider-middleware.html
"""

BOT_NAME = "jpbox_scraper"

SPIDER_MODULES = ["jpbox_scraper.spiders"]
NEWSPIDER_MODULE = "jpbox_scraper.spiders"

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = "jpbox_scraper (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False  # Set to False to bypass robots.txt restrictions (use responsibly).

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#     "Accept-Language": "en",
# }

# Enable or disable spider middlewares
# SPIDER_MIDDLEWARES = {
#     "jpbox_scraper.middlewares.JpboxScraperSpiderMiddleware": 543,
# }

# Enable or disable downloader middlewares
# DOWNLOADER_MIDDLEWARES = {
#     "jpbox_scraper.middlewares.JpboxScraperDownloaderMiddleware": 543,
# }

# Enable or disable extensions
# EXTENSIONS = {
#     "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Configure item pipelines
# ITEM_PIPELINES = {
#     "jpbox_scraper.pipelines.JpboxScraperPipeline": 300,
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# AUTOTHROTTLE_ENABLED = True
# AUTOTHROTTLE_START_DELAY = 5  # Initial download delay
# AUTOTHROTTLE_MAX_DELAY = 60  # Maximum download delay in case of high latencies
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0  # Average number of requests sent in parallel
# AUTOTHROTTLE_DEBUG = False  # Enable throttling stats for each response

# Enable and configure HTTP caching (disabled by default)
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = "httpcache"
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"  # Ensure UTF-8 encoding for exported files.

# Custom user agent for the scraper
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

# Configure export settings for CSV output
FEEDS = {
    "films.csv": {
        "format": "csv",  # Export format
        "encoding": "utf8",  # File encoding
        "overwrite": True,  # Overwrite the file if it exists
    }
}

# Custom settings for debugging and encoding
custom_settings = {
    "DUPEFILTER_DEBUG": True,  # Enable duplicate filter debugging
    "FEED_EXPORT_ENCODING": "utf-8",  # Ensure UTF-8 encoding for feeds
}
