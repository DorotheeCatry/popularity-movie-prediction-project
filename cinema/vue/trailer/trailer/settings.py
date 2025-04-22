BOT_NAME = "trailer"
SPIDER_MODULES = ["trailer.spiders"]
NEWSPIDER_MODULE = "trailer.spiders"
ROBOTSTXT_OBEY = False

DOWNLOAD_DELAY = 0.5
AUTOTHROTTLE_ENABLED = False

USER_AGENT_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:111.0) Gecko/20100101 Firefox/111.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2_1) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/16.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.0.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_3 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Mobile/15E148 Safari/604.1",
]

DOWNLOADER_MIDDLEWARES = {
    "trailer.middlewares.RotateUserAgentMiddleware": 400,
    #"scrapy_playwright.middleware.PlaywrightMiddleware": 800,
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
}

DOWNLOAD_HANDLERS = {
    "http":  "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_LAUNCH_OPTIONS = {"headless": True}

ITEM_PIPELINES = {
    "trailer.pipelines.CleanTrailerPipeline": 300,
}

FEEDS = {
    "trailers.csv": {
        "format":    "csv",
        "fields":    ["titre", "vues", "date_sortie"],
        "overwrite": True,
        "encoding":  "utf-8",
    }
}

LOG_LEVEL = "INFO"

