# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CinescrapingItem(scrapy.Item):
    
    title = scrapy.Field()
    genre = scrapy.Field()
    date = scrapy.Field()
    time = scrapy.Field()
    realisator = scrapy.Field()
    actors = scrapy.Field()
    scenario = scrapy.Field()
    production = scrapy.Field()
    music = scrapy.Field()
    director = scrapy.Field()
    country = scrapy.Field()
    language = scrapy.Field()
    budget = scrapy.Field()
    box_office = scrapy.Field()
    week_1 = scrapy.Field() #target
    critics = scrapy.Field()
    url_movie = scrapy.Field()
    classification = scrapy.Field() 


