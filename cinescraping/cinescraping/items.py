# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CinescrapingItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    genre = scrapy.Field()
    date = scrapy.Field()
    time = scrapy.Field()
    realisator = scrapy.Field()
    actors = scrapy.Field()
    scenario = scrapy.Field()
    production = scrapy.Field()
    music = scrapy.Field()

