import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from datetime import datetime
import re
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.selector import Selector
from ..items import MovieReleaseScraperParsingItem
from ..utils import parse_date

class AllocineSpider(CrawlSpider):
    name = 'allocine'
    allowed_domains = ['allocine.fr']
    start_urls = ['https://www.allocine.fr/film/aucinema/']
    
    custom_settings = {
        'ITEM_PIPELINES': {
            'scraping_module.allocine_scraper.pipelines.ReleaseDatabasePipeline': 300,
        }
    }

    rules = (
        Rule(LinkExtractor(restrict_xpaths="//a[@class='meta-title-link']"), callback='parse_film', follow=True),
    )

    def __init__(self, *args, **kwargs):
        super(AllocineSpider, self).__init__(*args, **kwargs)
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-ads")
        chrome_options.add_argument("--disable-extensions")
        
        try:
            chrome_options.binary_location = "/usr/bin/chromium-browser"
            self.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            self.logger.error(f"Error initializing Chrome with specified binary location: {e}")
            chrome_options.binary_location = ""
            self.driver = webdriver.Chrome(options=chrome_options)
        
        self.logger.info("Chrome WebDriver initialized successfully")

    def start_requests(self):
        self.logger.info("Starting requests")
        try:
            self.driver.get(self.start_urls[0])
            
            try:
                self.driver.execute_script("document.getElementById('didomi-popup').style.display='none';")
                self.logger.info("Popup dismissed")
            except Exception as e:
                self.logger.warning(f"Could not dismiss popup: {e}")
            
            yield scrapy.Request(
                url=self.driver.current_url,
                callback=self.parse,
                dont_filter=True
            )
        except Exception as e:
            self.logger.error(f"Error in start_requests: {e}")

    def parse_film(self, response):
        self.logger.info(f"Parsing film: {response.url}")
        
        try:
            self.driver.get(response.url)
            
            try:
                self.driver.execute_script("document.getElementById('didomi-popup').style.display='none';")
            except Exception:
                pass
            
            item = MovieReleaseScraperParsingItem()
            
            # Basic info
            item['title'] = response.xpath("//div[@class='titlebar-title titlebar-title-xl']/text()").get()
            self.logger.info(f"Processing movie: {item['title']}")
            
            item['original_title'] = response.xpath('//span[normalize-space(text())="Titre original"]/following-sibling::span/text()').get()
            if item['original_title']:
                item['original_title'] = item['original_title'].strip()
            
            release_date = response.xpath("//span[@property='datePublished']/text()").get()
            if release_date:
                item['release_date'] = parse_date(release_date.strip())
            
            item['duration'] = response.xpath("//div[@class='meta-body-item meta-body-info']//text()[contains(., 'h') and contains(., 'min')]").get()
            if item['duration']:
                item['duration'] = item['duration'].strip()
            
            item['genres'] = response.xpath("//div[contains(@class, 'meta-body-info')]//span[contains(@class, 'dark-grey-link')]/text()").getall()
            
            # Ratings
            ratings = response.xpath("//div[@class='stareval stareval-small stareval-theme-default']/span[@class='stareval-note']/text()").getall()
            item['press_rating'] = ratings[0] if len(ratings) > 0 else None
            item['audience_rating'] = ratings[1] if len(ratings) > 1 else None
            
            # Cast & crew
            item['director'] = response.xpath("//div[@class='meta-body-item meta-body-direction meta-body-oneline']/span[normalize-space(text())='De']/following-sibling::span/text()").getall()
            item['writer'] = response.xpath("//div[@class='meta-body-item meta-body-direction meta-body-oneline']/span[normalize-space(text())='Par']/following-sibling::span/text()").getall()
            
            # Other details
            item['audience'] = response.xpath("//div[@class='certificate']/span[@class='certificate-text']/text()").get()
            item['audience'] = item['audience'].strip() if item['audience'] else None
            
            item['distributor'] = response.xpath("//section[@class='section ovw ovw-technical']//span[text()='Distributeur']/following-sibling::span/text()").get()
            item['distributor'] = item['distributor'].strip() if item['distributor'] else None
            
            item['movie_type'] = response.xpath("//section[@class='section ovw ovw-technical']//span[text()='Type de film']/following-sibling::span/text()").get()
            item['movie_type'] = item['movie_type'].strip() if item['movie_type'] else None
            
            item['nationality'] = response.css("div.item span.what.light:contains('Nationalité') + span span.nationality::text").getall()
            
            item['languages'] = response.xpath("//section[@class='section ovw ovw-technical']//span[text()='Langues']/following-sibling::span/text()").getall()
            
            # Content
            item['synopsis'] = response.xpath("//p[@class='bo-p']/text()").get()
            item['actors'] = response.xpath("//div[contains(@class, 'meta-body-item meta-body-actor')]//span[contains(@class, 'dark-grey-link')]/text()").getall()
            
            # Box office data
            box_office_url = response.url.replace('_gen_cfilm=', '-').replace('.html', '/box-office/')
            yield scrapy.Request(
                url=box_office_url,
                callback=self.parse_boxoffice,
                meta={'item': item},
                dont_filter=True
            )
            
        except Exception as e:
            self.logger.error(f"Error in parse_film: {e}")

    def parse_boxoffice(self, response):
        self.logger.info(f"Parsing box office page: {response.url}")
        
        try:
            item = response.meta['item']
            
            box_office_fr = response.xpath('//h2[contains(text(), "Box Office France")]/parent::div/following-sibling::table[1]//tr[position() = 1]/td[2]/text()').get()
            if box_office_fr:
                item['box_office_fr'] = box_office_fr.strip()
            
            box_office_us = response.xpath('//h2[contains(text(), "Box Office US")]/parent::div/following-sibling::table[1]//tr[position() = 1]/td[2]/text()').get()
            if box_office_us:
                item['box_office_us'] = box_office_us.strip()
            
            yield item
            
        except Exception as e:
            self.logger.error(f"Error in parse_boxoffice: {e}")
            if 'item' in response.meta:
                yield response.meta['item']
    
    def closed(self, reason):
        self.logger.info(f"Spider closed: {reason}")
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()
            self.logger.info("Selenium driver closed")