from allocine_scraper.items import FilmscraperParsingItem
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import scrapy

class FilmspiderSpider(CrawlSpider):
    name = "filmspider"
    allowed_domains = ["allocine.fr"]
    start_urls = ["https://allocine.fr/films/?page="+str(x) for x in range(1, 2)]

    
    rules = (
        Rule(LinkExtractor(restrict_xpaths=".//a[@class='meta-title-link']"),
             callback='parse_film'),
    )
    
    def parse_film(self , response):
        item = FilmscraperParsingItem()
        
        item['titre'] = response.xpath("//div[@class='titlebar-title titlebar-title-xl']/text()").get()
        item['titre_original'] = response.xpath("//div[@class='meta-body-item']/span/text()").getall()
        item['infos'] = response.xpath("//div[@class='meta-body-item meta-body-info']/span/text()").getall()
        item['infos_technique'] = response.xpath("//section[@class='section ovw ovw-technical']/div/span/text()").getall()
        item['realisateur'] = response.xpath("//div[@class='meta-body-item meta-body-direction meta-body-oneline']/span/text()").getall()
        item['only_realisateur'] = response.xpath("//div[@class='meta-body-item meta-body-direction ']/span/text()").getall()
        item['nationalite'] = response.xpath("//section[@class='section ovw ovw-technical']/div/span/span/text()").getall()
        item['description'] = response.xpath("//p[@class='bo-p']/text()").getall()
        item['ratings'] = response.xpath("//div[@class='stareval stareval-small stareval-theme-default']/span[@class='stareval-note']/text()").getall()
        item['duration'] = response.xpath("//div[@class='meta-body-item meta-body-info']/text()").getall()
        item['public'] = response.xpath("//div[@class='certificate']/span[@class='certificate-text']/text()").get()
        item['type'] = 'raw'
        
        header = response.xpath("//div[@class='item-center']/text()").getall()
        
        if 'Casting' in header:
            casting_url = response.url.replace('_gen_cfilm=', '-').replace('.html', '/casting/')
            yield scrapy.Request(casting_url, meta={'meta_item': item}, callback=self.parse_acteurs)
        else:
            item['acteurs'] = []
            yield item
        
    def parse_acteurs(self, response):
        item = response.meta['meta_item']
        
        item['acteurs'] = response.xpath("//section[@class='section casting-actor']/div/div/div/div//text()").getall()

        yield item