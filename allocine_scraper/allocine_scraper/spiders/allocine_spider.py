import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from allocine_scraper.items import AllocineScraperParsingItem

class AllocineSpider(CrawlSpider):
    name = "allocinespider"
    allowed_domains = ["allocine.fr"]
    start_urls = ["https://allocine.fr/films/?page=" + str(x) for x in range(1, 2)]
    custom_settings = {
    'ITEM_PIPELINES' : {
        "allocine_scraper.pipelines.AllocineDatabasePipeline": 300
    }
}

    rules = (
        Rule(LinkExtractor(restrict_xpaths=".//a[@class='meta-title-link']"), callback='parse_film'),
    )

    def parse_film(self, response):
        item = AllocineScraperParsingItem()
        
        item['title'] = response.xpath("//div[@class='titlebar-title titlebar-title-xl']/text()").get()
        item['original_title'] = response.xpath('//span[normalize-space(text())="Titre original"]/following-sibling::span/text()').get()
        if item['original_title']:
            item['original_title'] = item['original_title'].strip()
        else:
            item['original_title'] = None

        item['release_date'] = response.xpath('//*[contains(@class, "date")]/text()').get()
        if item['release_date']:
            item['release_date'] = item['release_date'].strip()
        else:
            item['release_date'] = None

        item['duration'] = response.xpath("//div[@class='meta-body-item meta-body-info']//text()[contains(., 'h') and contains(., 'min')]").get()
        if item['duration']:
            item['duration'] = item['duration'].strip()
        else:
            item['duration'] = None

        item['genres'] = response.xpath("//div[contains(@class, 'meta-body-info')]//span[contains(@class, 'dark-grey-link')]/text()").getall()
        if not item['genres']:
            item['genres'] = None

        ratings = response.xpath("//div[@class='stareval stareval-small stareval-theme-default']/span[@class='stareval-note']/text()").getall()
        item['press_rating'] = ratings[0] if len(ratings) > 0 else None
        item['audience_rating'] = ratings[1] if len(ratings) > 1 else None

        item['director'] = response.xpath("//div[@class='meta-body-item meta-body-direction meta-body-oneline']/span[normalize-space(text())='De']/following-sibling::span/text()").get()
        if not item['director']:
            item['director'] = None

        item['writer'] = response.xpath("//div[@class='meta-body-item meta-body-direction meta-body-oneline']/span[normalize-space(text())='Par']/following-sibling::span/text()").get()
        if not item['writer']:
            item['writer'] = None

        item['audience'] = response.xpath("//div[@class='certificate']/span[@class='certificate-text']/text()").get()
        if not item['audience']:
            item['audience'] = None

        item['distributor'] = response.xpath("//section[@class='section ovw ovw-technical']//span[text()='Distributeur']/following-sibling::span/text()").get()
        if not item['distributor']:
            item['distributor'] = None

        item['movie_type'] = response.xpath("//section[@class='section ovw ovw-technical']//span[text()='Type de film']/following-sibling::span/text()").get()
        if not item['movie_type']:
            item['movie_type'] = None

        item['nationality'] = response.css("div.item span.what.light:contains('Nationalité') + span span.nationality::text").get()
        if not item['nationality']:
            item['nationality'] = None

        item['languages'] = response.xpath("//section[@class='section ovw ovw-technical']//span[text()='Langues']/following-sibling::span/text()").get()
        if item['languages']:
            item['languages'] = item['languages'].strip()
        else:
            item['languages'] = None

        item['synopsis'] = response.xpath("//p[@class='bo-p']/text()").getall()
        if not item['synopsis']:
            item['synopsis'] = None
            
        item['actors'] = response.xpath("//div[contains(@class, 'meta-body-item meta-body-actor')]//span[contains(@class, 'dark-grey-link')]/text()").getall()
        if not item['actors']:
            item['actors'] = None
            
        yield item