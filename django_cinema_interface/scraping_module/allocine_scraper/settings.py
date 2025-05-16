import random

BOT_NAME = "allocine_scraper"

SPIDER_MODULES = ["scraping_module.allocine_scraper.spiders"]
NEWSPIDER_MODULE = "scraping_module.allocine_scraper.spiders"

LOG_LEVEL = 'DEBUG'

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"

ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = 4

DOWNLOAD_DELAY = random.uniform(0.5, 1.5)

RANDOMIZE_DOWNLOAD_DELAY = True

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
}

ITEM_PIPELINES = {
    'scraping_module.allocine_scraper.pipelines.ReleaseDatabasePipeline': 300,
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"