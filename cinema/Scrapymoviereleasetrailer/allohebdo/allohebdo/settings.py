BOT_NAME = "allohebdo"
SPIDER_MODULES = ["allohebdo.spiders"]
NEWSPIDER_MODULE = "allohebdo.spiders"

# ---------- Politesse / perf ----------
ROBOTSTXT_OBEY      = True
CONCURRENT_REQUESTS = 8
DOWNLOAD_DELAY      = 0.5
AUTOTHROTTLE_ENABLED      = True
AUTOTHROTTLE_START_DELAY  = 1
AUTOTHROTTLE_MAX_DELAY    = 10

# ---------- User-Agent ----------
USER_AGENT_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]
DOWNLOADER_MIDDLEWARES = {
    "allohebdo.middlewares.RandomUserAgentMiddleware": 400,
}

# ---------- Pipelines ----------
ITEM_PIPELINES = {
    "allohebdo.pipelines.CleanItemPipeline": 300,
    "allohebdo.pipelines.DedupPipeline":    400,
}

# ---------- Export ----------
FEEDS = {
    "films.csv": {
        "format": "csv",
        "overwrite": True,
        "encoding": "utf-8",
    },
}
FEED_EXPORT_ENCODING = "utf-8"
LOG_LEVEL = "INFO"














