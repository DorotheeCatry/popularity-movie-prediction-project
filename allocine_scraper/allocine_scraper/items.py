import scrapy
from scrapy import Field
import scrapy.item

class AllocineScraperParsingItem(scrapy.Item):
    title = Field()
    original_title = Field()
    release_date = Field()
    duration = Field()
    genres = Field()
    press_rating = Field()
    audience_rating = Field()
    director = Field()
    writer = Field()
    audience = Field()
    distributor = Field()
    movie_type = Field()
    nationality = Field()
    languages = Field()
    synopsis = Field()
    actors = Field()
