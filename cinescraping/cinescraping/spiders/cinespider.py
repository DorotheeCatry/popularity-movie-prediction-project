import scrapy


class CinespiderSpider(scrapy.Spider):
    name = "cinespider"
    allowed_domains = ["allocine.fr"]
    start_urls = ["https://allocine.fr"]

    def parse(self, response):
        movies = response.css('a.meta-title-link::text')

        for movie in movies:
            yield {
                "title": movie.css('a.meta-title-link::text').get(),
,            }
