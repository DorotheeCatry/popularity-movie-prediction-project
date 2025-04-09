JOBDIR = 'jobdir'

BOT_NAME = "movies_scraping"
SPIDER_MODULES = ["movies_scraping.spiders"]
NEWSPIDER_MODULE = "movies_scraping.spiders"
# Respecter les règles du robots.txt
ROBOTSTXT_OBEY = True
# Augmenter le nombre total de requêtes simultanées pour gagner en rapidité
CONCURRENT_REQUESTS = 32
# Limiter le nombre de requêtes par domaine et par IP pour éviter la surchage d'un même serveur
CONCURRENT_REQUESTS_PER_DOMAIN = 8
CONCURRENT_REQUESTS_PER_IP = 8
# Réduire légèrement le délai entre les requêtes pour plus de rapidité, en laissant l'autothrottle ajuster au besoin
DOWNLOAD_DELAY = 0.25
# Désactiver les cookies si non nécessaires
COOKIES_ENABLED = False
# -----------------------------------------------------------------------------
# Configuration des middlewares de téléchargement : rotation des User Agents
# -----------------------------------------------------------------------------
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
}
# Liste de User Agents variés pour la rotation automatique
USER_AGENT_LIST = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0',
    'Mozilla/5.0 (Windows NT 6.1; rv:65.0) Gecko/20100101 Firefox/65.0',
    'Mozilla/5.0 (Windows NT 6.3; Trident/7.0; AS; Lumia 920) like Gecko',
    'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Mobile Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0',
    'Mozilla/5.0 (Windows NT 5.1; rv:40.0) Gecko/20100101 Firefox/40.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
    'Mozilla/5.0 (Linux; U; Android 4.2.2; en-us; GT-I9300 Build/JDQ39) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; rv:31.0) Gecko/20100101 Firefox/31.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'
]
# -----------------------------------------------------------------------------
# Configuration de pipelines : ici, nous utilisons un pipeline CSV personnalisé
# -----------------------------------------------------------------------------
# ITEM_PIPELINES = {
#}
# -----------------------------------------------------------------------------
# AutoThrottle permet d'adapter dynamiquement le rythme des requêtes pour éviter le blocage
# -----------------------------------------------------------------------------
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0.5      # Délai initial réduit pour démarrer rapidement
AUTOTHROTTLE_MAX_DELAY = 5          # Délai maximal en cas de latence
AUTOTHROTTLE_TARGET_CONCURRENCY = 4.0  # Viser 4 requêtes simultanées par serveur
# -----------------------------------------------------------------------------
# Paramètres relatifs au threadpool (augmenter légèrement si nécessaire)
# -----------------------------------------------------------------------------
REACTOR_THREADPOOL_MAXSIZE = 20
# -----------------------------------------------------------------------------
# Pour garantir la compatibilité avec les versions futures de Scrapy,
# utilisez le réacteur asynchrone AsyncioSelectorReactor.
# -----------------------------------------------------------------------------
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"