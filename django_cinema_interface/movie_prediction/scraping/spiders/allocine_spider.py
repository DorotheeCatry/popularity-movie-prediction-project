import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from datetime import datetime
import re

class AllocineSpider(CrawlSpider):
    name = 'allocine'
    allowed_domains = ['allocine.fr']
    start_urls = ['https://www.allocine.fr/film/aucinema/']
    
    rules = (
        Rule(
            LinkExtractor(restrict_xpaths="//h2[@class='meta-title']/a"),
            callback='parse_movie',
            follow=True
        ),
    )
    
    def parse_movie(self, response):
        title = response.xpath("//h1[@class='title-entity']/text()").get()
        release_date = response.xpath("//span[@property='datePublished']/text()").get()
        duration = response.xpath("//div[@class='meta-body-item meta-body-info']/text()").get()
        
        # Clean and process the data
        if release_date:
            try:
                release_date = datetime.strptime(release_date.strip(), '%d %B %Y').date()
            except ValueError:
                release_date = None
                
        if duration:
            duration = duration.strip()
            
        return {
            'title': title.strip() if title else None,
            'release_date': release_date,
            'duration': duration,
        }