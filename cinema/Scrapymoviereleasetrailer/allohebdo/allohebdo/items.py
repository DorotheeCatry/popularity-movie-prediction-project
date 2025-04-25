# allohebdo/items.py
import scrapy


class FilmItem(scrapy.Item):
    title         = scrapy.Field()
    release_date  = scrapy.Field()   # 'YYYY-MM-DD'
    duration      = scrapy.Field()   # '1h 45min'
    genres        = scrapy.Field()   # list[str]
    director      = scrapy.Field()
    actors        = scrapy.Field()   # list[str]
    writer        = scrapy.Field()   # optionnel
    producers     = scrapy.Field()   # list[str]
    distributor   = scrapy.Field()   # optionnel
    synopsis      = scrapy.Field()
    sessions      = scrapy.Field()   # int
    trailer_views = scrapy.Field()   # int


