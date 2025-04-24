import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from allocine_scraper.items import AllocineScraperParsingItem

class AllocineSpider(CrawlSpider):
    """
    AllocineSpider is a Scrapy spider designed to scrape movie data from the Allocine website.
    Attributes:
        name (str): The name of the spider.
        allowed_domains (list): A list of allowed domains for the spider.
        start_urls (list): A list of URLs to start crawling from.
        custom_settings (dict): Custom settings for the spider, including the pipeline configuration.
    Rules:
        rules (tuple): A tuple defining the crawling rules. It extracts links to movie pages using XPath and processes them with the `parse_film` callback.
    Methods:
        parse_film(response):
            Parses movie details from the movie page. Extracts information such as title, original title, release date, duration, genres, ratings, director, writer, audience, distributor, movie type, nationality, languages, synopsis, actors, and image URL. If the movie has a "Box Office" section, it generates a request to parse box office data.
        parse_boxoffice(response):
            Parses box office data from the box office page. Extracts information about the French and US box office performance of the movie.
    Usage:
        This spider is used to scrape detailed movie information and box office data from Allocine. It is configured to store the scraped data using a custom pipeline.
    """
    name = "allocinespider"
    allowed_domains = ["allocine.fr"]
    start_urls = ["https://allocine.fr/films/?page=" + str(x) for x in range(1, 8000)]
    custom_settings = {
    'ITEM_PIPELINES' : {
        "allocine_scraper.pipelines.AllocineDatabasePipeline": 300
    }
}

    rules = (
        Rule(LinkExtractor(restrict_xpaths=".//a[@class='meta-title-link']"), callback='parse_film'),
    )

    def parse_film(self, response):
        """ Parse only movies that have a Box Office tab """
        header = response.xpath("//div[@class='item-center']/text()").getall()
        
        if 'Box Office' in header:
            item = AllocineScraperParsingItem()

            # Title
            item['title'] = response.xpath("//div[@class='titlebar-title titlebar-title-xl']/text()").get()
            item['title'] = item['title'].strip() if item['title'] else None

            # Original title
            item['original_title'] = response.xpath('//span[normalize-space(text())="Titre original"]/following-sibling::span/text()').get()
            item['original_title'] = item['original_title'].strip() if item['original_title'] else None

            # Release date
            item['release_date'] = response.xpath('//*[contains(@class, "date")]/text()').get()
            item['release_date'] = item['release_date'].strip() if item['release_date'] else None

            # Duration
            item['duration'] = response.xpath("//div[@class='meta-body-item meta-body-info']//text()[contains(., 'h') and contains(., 'min')]").get()
            item['duration'] = item['duration'].strip() if item['duration'] else None

            # Genres
            item['genres'] = response.xpath("//div[contains(@class, 'meta-body-info')]//span[contains(@class, 'dark-grey-link')]/text()").getall()
            item['genres'] = [genre.strip() for genre in item['genres']] if item['genres'] else None

            # Ratings (press rating and audience rating)
            ratings = response.xpath("//div[@class='stareval stareval-small stareval-theme-default']/span[@class='stareval-note']/text()").getall()
            if ratings:
                item['press_rating'] = ratings[0].strip() if ratings[0] else None
                item['audience_rating'] = ratings[1].strip() if len(ratings) > 1 else None
            else:
                item['press_rating'] = item['audience_rating'] = None

            # Director
            item['director'] = response.xpath("//div[@class='meta-body-item meta-body-direction meta-body-oneline']/span[normalize-space(text())='De']/following-sibling::span/text()").getall()
            item['director'] = [director.strip() for director in item['director']] if item['director'] else None

            # Writer
            item['writer'] = response.xpath("//div[@class='meta-body-item meta-body-direction meta-body-oneline']/span[normalize-space(text())='Par']/following-sibling::span/text()").getall()
            item['writer'] = [writer.strip() for writer in item['writer']] if item['writer'] else None

            # Audience
            item['audience'] = response.xpath("//div[@class='certificate']/span[@class='certificate-text']/text()").get()
            item['audience'] = item['audience'].strip() if item['audience'] else None

            # Distributor
            item['distributor'] = response.xpath("//section[@class='section ovw ovw-technical']//span[text()='Distributeur']/following-sibling::span/text()").get()
            item['distributor'] = item['distributor'].strip() if item['distributor'] else None

            # Movie type
            item['movie_type'] = response.xpath("//section[@class='section ovw ovw-technical']//span[text()='Type de film']/following-sibling::span/text()").get()
            item['movie_type'] = item['movie_type'].strip() if item['movie_type'] else None

            # Nationality
            item['nationality'] = response.css("div.item span.what.light:contains('Nationalité') + span span.nationality::text").getall()
            item['nationality'] = [nationality.strip() for nationality in item['nationality']] if item['nationality'] else None

            # Languages
            item['languages'] = response.xpath("//section[@class='section ovw ovw-technical']//span[text()='Langues']/following-sibling::span/text()").getall()
            item['languages'] = [lang.strip() for lang in item['languages']] if item['languages'] else None

            # Synopsis
            item['synopsis'] = response.xpath("//p[@class='bo-p']/text()").get()
            item['synopsis'] = item['synopsis'].strip() if item['synopsis'] else None

            # Actors
            item['actors'] = response.xpath("//div[contains(@class, 'meta-body-item meta-body-actor')]//span[contains(@class, 'dark-grey-link')]/text()").getall()
            item['actors'] = [actor.strip() for actor in item['actors']] if item['actors'] else None

            # Image URL
            item['image_url'] = response.xpath("//img[@class='thumbnail-img']/@src").get()
            item['image_url'] = item['image_url'].strip() if item['image_url'] else None


            # Retrieve the Box Office URL
            boxoffice_url = response.url.replace('_gen_cfilm=', '-').replace('.html', '/box-office/')
            yield scrapy.Request(boxoffice_url, meta={'item': item}, callback=self.parse_boxoffice)

    def parse_boxoffice(self, response):
        """ Parse Box Office data """
        item = response.meta['item']

        # Box Office France
        box_office_fr = response.xpath('//h2[contains(text(), "Box Office France")]/parent::div/following-sibling::table[1]//tr[position() = 1]/td[2]/text()').get()
        item['box_office_fr'] = box_office_fr.strip() if box_office_fr else None

        # Box Office US
        box_office_us = response.xpath('//h2[contains(text(), "Box Office US")]/parent::div/following-sibling::table[1]//tr[position() = 1]/td[2]/text()').get()
        item['box_office_us'] = box_office_us.strip() if box_office_us else None

        yield item

