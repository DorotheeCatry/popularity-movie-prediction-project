import time
import scrapy
import re
from selenium.webdriver.common.by import By
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ..items import MovieReleaseScraperParsingItem
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.selector import Selector
from ..utils import parse_date

class NewReleaseMovieSpider(CrawlSpider):
    name = "newreleasespider"
    allowed_domains = ["allocine.fr"]
    start_urls = ["https://www.allocine.fr/film/agenda"]
    
    custom_settings = {
        'ITEM_PIPELINES': {
            'scraping_module.allocine_scraper.pipelines.ReleaseDatabasePipeline': 300,
        }
    }

    rules = (
        Rule(LinkExtractor(restrict_xpaths="//a[@class='meta-title-link']"), callback='parse_film', follow=True),
    )

    def __init__(self, *args, **kwargs):
        super(NewReleaseMovieSpider, self).__init__(*args, **kwargs)
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
            
            time.sleep(2)
            
            yield scrapy.Request(
                url=self.driver.current_url,
                callback=self.parse,
                dont_filter=True
            )
        except Exception as e:
            self.logger.error(f"Error in start_requests: {e}")

    def parse(self, response):
        self.logger.info(f"Parsing page: {response.url}")
        
        try:
            self.driver.get(response.url)
            
            try:
                self.driver.execute_script("document.getElementById('didomi-popup').style.display='none';")
            except Exception as e:
                self.logger.warning(f"Error dismissing popup: {e}")
            
            time.sleep(2)
            
            sel = Selector(text=self.driver.page_source)
            
            try:
                movie_release_element = response.xpath('//select[contains(@class, "dropdown-select-inner")]//option[@selected]/text()').get()
                if movie_release_element:
                    movie_release = parse_date(movie_release_element.strip())
                    self.logger.info(f"Current page release date: {movie_release}")
                else:
                    self.logger.warning("Could not find release date on page")
                    movie_release = None
            except Exception as e:
                self.logger.error(f"Error parsing release date: {e}")
                movie_release = None
            
            movie_links = sel.xpath("//a[@class='meta-title-link']/@href").getall()
            self.logger.info(f"Found {len(movie_links)} movie links")
            
            for link in movie_links:
                yield response.follow(link, callback=self.parse_film, meta={'movie_release': movie_release})
                
        except Exception as e:
            self.logger.error(f"Error in parse method: {e}")

    def parse_film(self, response):
        self.logger.info(f"Parsing film: {response.url}")
        
        try:
            self.driver.get(response.url)
            
            try:
                self.driver.execute_script("document.getElementById('didomi-popup').style.display='none';")
            except Exception:
                pass
            
            time.sleep(2)
            
            movie_release = response.meta.get('movie_release')
            
            try:
                movie_date_element = response.xpath('//*[contains(@class, "date")]/text()').get()
                if movie_date_element:
                    movie_date = parse_date(movie_date_element.strip())
                else:
                    movie_date = None
            except Exception as e:
                self.logger.error(f"Error parsing movie date: {e}")
                movie_date = None
            
            if movie_release and movie_date and movie_date != movie_release:
                self.logger.info(f"Skipping movie with non-matching release date: {movie_date} != {movie_release}")
                return
            
            item = MovieReleaseScraperParsingItem()
            
            item['title'] = response.xpath("//div[@class='titlebar-title titlebar-title-xl']/text()").get()
            self.logger.info(f"Processing movie: {item['title']}")
            
            item['original_title'] = response.xpath('//span[normalize-space(text())="Titre original"]/following-sibling::span/text()').get()
            if item['original_title']:
                item['original_title'] = item['original_title'].strip()
            
            item['release_date'] = movie_date_element.strip() if movie_date_element else None
            
            item['duration'] = response.xpath("//div[@class='meta-body-item meta-body-info']//text()[contains(., 'h') and contains(., 'min')]").get()
            if item['duration']:
                item['duration'] = item['duration'].strip()
            
            item['genres'] = response.xpath("//div[contains(@class, 'meta-body-info')]//span[contains(@class, 'dark-grey-link')]/text()").getall()
            
            ratings = response.xpath("//div[@class='stareval stareval-small stareval-theme-default']/span[@class='stareval-note']/text()").getall()
            item['press_rating'] = ratings[0] if len(ratings) > 0 else None
            item['audience_rating'] = ratings[1] if len(ratings) > 1 else None
            
            item['director'] = response.xpath("//div[@class='meta-body-item meta-body-direction meta-body-oneline']/span[normalize-space(text())='De']/following-sibling::span/text()").getall()
            item['writer'] = response.xpath("//div[@class='meta-body-item meta-body-direction meta-body-oneline']/span[normalize-space(text())='Par']/following-sibling::span/text()").getall()
            
            item['audience'] = response.xpath("//div[@class='certificate']/span[@class='certificate-text']/text()").get()
            item['audience'] = item['audience'].strip() if item['audience'] else None
            
            item['distributor'] = response.xpath("//section[@class='section ovw ovw-technical']//span[text()='Distributeur']/following-sibling::span/text()").get()
            item['distributor'] = item['distributor'].strip() if item['distributor'] else None
            
            item['movie_type'] = response.xpath("//section[@class='section ovw ovw-technical']//span[text()='Type de film']/following-sibling::span/text()").get()
            item['movie_type'] = item['movie_type'].strip() if item['movie_type'] else None
            
            item['nationality'] = response.css("div.item span.what.light:contains('Nationalité') + span span.nationality::text").getall()
            
            item['languages'] = response.xpath("//section[@class='section ovw ovw-technical']//span[text()='Langues']/following-sibling::span/text()").getall()
            
            item['synopsis'] = response.xpath("//p[@class='bo-p']/text()").get()
            item['actors'] = response.xpath("//div[contains(@class, 'meta-body-item meta-body-actor')]//span[contains(@class, 'dark-grey-link')]/text()").getall()
            
            try:
                showings_element = self.driver.find_element(By.XPATH, "//a[contains(@class, 'button-inverse-full')]//span[contains(@class, 'txt')]")
                item['showings'] = showings_element.text.strip()
            except Exception:
                item['showings'] = None
            
            item['image_url'] = response.xpath("//img[@class='thumbnail-img']/@src").get()
            
            header_texts = response.xpath("//div[@class='item-center']/text()").getall()
            
            if 'Bandes-annonces' in header_texts:
                try:
                    trailer_link = self.driver.find_element(By.XPATH, "//a[contains(@title, 'Bandes-annonces')]")
                    trailer_link.click()
                    
                    try:
                        self.driver.execute_script("document.getElementById('didomi-popup').style.display='none';")
                    except Exception:
                        pass
                    
                    time.sleep(2)
                    
                    trailer_page_url = self.driver.current_url
                    
                    yield scrapy.Request(
                        url=trailer_page_url,
                        callback=self.parse_trailer,
                        meta={'meta_item': item},
                        dont_filter=True
                    )
                    return
                except Exception as e:
                    self.logger.error(f"Error clicking trailer link: {e}")
            
            if 'Box Office' in header_texts:
                box_office_url = response.url.replace('_gen_cfilm=', '-').replace('.html', '/box-office/')
                yield scrapy.Request(
                    url=box_office_url,
                    callback=self.parse_boxoffice,
                    meta={'meta_item': item},
                    dont_filter=True
                )
                return
            
            yield item
            
        except Exception as e:
            self.logger.error(f"Error in parse_film: {e}")

    def parse_trailer(self, response):
        self.logger.info(f"Parsing trailer page: {response.url}")
        
        try:
            item = response.meta['meta_item']
            
            item['trailer_date'] = response.xpath("//div[contains(@class, 'media-info-item') and contains(@class, 'icon-time')]/text()").get()
            if item['trailer_date']:
                item['trailer_date'] = item['trailer_date'].strip()
            
            item['trailer_number'] = response.css('div.titlebar-title::text').get()
            if item['trailer_number']:
                item['trailer_number'] = item['trailer_number'].strip()
            
            item['trailer_views'] = response.xpath("//div[contains(@class, 'media-info-item') and contains(@class, 'icon-eye')]/text()").get()
            if item['trailer_views']:
                item['trailer_views'] = item['trailer_views'].strip()
            
            header_texts = response.xpath("//div[@class='item-center']/text()").getall()
            if 'Box Office' in header_texts:
                box_office_url = response.url.replace('/video/', '/').replace('_gen_cfilm=', '-').replace('.html', '/box-office/')
                yield scrapy.Request(
                    url=box_office_url,
                    callback=self.parse_boxoffice,
                    meta={'meta_item': item},
                    dont_filter=True
                )
                return
            
            yield item
            
        except Exception as e:
            self.logger.error(f"Error in parse_trailer: {e}")
            if 'meta_item' in response.meta:
                yield response.meta['meta_item']

    def parse_boxoffice(self, response):
        self.logger.info(f"Parsing box office page: {response.url}")
        
        try:
            item = response.meta['meta_item']
            
            box_office_fr = response.xpath('//h2[contains(text(), "Box Office France")]/parent::div/following-sibling::table[1]//tr[position() = 1]/td[2]/text()').get()
            if box_office_fr:
                item['box_office_fr'] = box_office_fr.strip()
            
            box_office_us = response.xpath('//h2[contains(text(), "Box Office US")]/parent::div/following-sibling::table[1]//tr[position() = 1]/td[2]/text()').get()
            if box_office_us:
                item['box_office_us'] = box_office_us.strip()
            
            yield item
            
        except Exception as e:
            self.logger.error(f"Error in parse_boxoffice: {e}")
            if 'meta_item' in response.meta:
                yield response.meta['meta_item']
    
    def closed(self, reason):
        self.logger.info(f"Spider closed: {reason}")
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()
            self.logger.info("Selenium driver closed")