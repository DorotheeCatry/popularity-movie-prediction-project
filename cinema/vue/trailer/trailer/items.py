import scrapy

class TrailerItem(scrapy.Item):
    titre       = scrapy.Field()
    vues        = scrapy.Field()
    date_sortie = scrapy.Field()
