import scrapy
import re
import time
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from allocine_scraper.items import AllocineScraperParsingItem
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class AllocineSpider(CrawlSpider):
    name = "allocinespider"
    allowed_domains = ["allocine.fr"]
    start_urls = [f"https://allocine.fr/films/?page={x}" for x in range(1, 3)]

    custom_settings = {
        'ITEM_PIPELINES': {
            "allocine_scraper.pipelines.AllocineDatabasePipeline": 300
        }
    }

    rules = (
        Rule(LinkExtractor(restrict_xpaths=".//a[@class='meta-title-link']"), callback='parse_film', follow=True),
    )

    def __init__(self, *args, **kwargs):
        super(AllocineSpider, self).__init__(*args, **kwargs)
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode for servers
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-ads")
        chrome_options.add_argument("--disable-extensions")
        
        # Set binary location if needed
        try:
            # Try to find chromium browser binary
            chrome_options.binary_location = "/usr/bin/chromium-browser"
            self.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            self.logger.error(f"Error initializing Chrome with specified binary location: {e}")
            # Fallback to default Chrome binary location
            chrome_options.binary_location = ""
            self.driver = webdriver.Chrome(options=chrome_options)
        
        self.logger.info("Chrome WebDriver initialized successfully")

    def parse_film(self, response):
        item = AllocineScraperParsingItem()
        
        header_texts = response.xpath("//div[@class='item-center']/text()").getall()
        
        try:
            if 'Box Office' in header_texts:
                # Basic info
                item['title'] = response.xpath("//div[@class='titlebar-title titlebar-title-xl']/text()").get()
                self.logger.info(f"Processing movie: {item['title']}")
                
                item['original_title'] = response.xpath('//span[normalize-space(text())="Titre original"]/following-sibling::span/text()').get()
                if item['original_title']:
                    item['original_title'] = item['original_title'].strip()
                
                # Release date
                item['release_date'] = response.xpath('//*[contains(@class, "date")]/text()').get()
                item['release_date'] = item['release_date'].strip() if item['release_date'] else None
                
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
                
                # Showing data
                try:
                    showings_element = self.driver.find_element(By.XPATH, "//a[contains(@class, 'button-inverse-full')]//span[contains(@class, 'txt')]")
                    item['showings'] = showings_element.text.strip()
                except Exception:
                    item['showings'] = None
                
                # Image
                item['image_url'] = response.xpath("//img[@class='thumbnail-img']/@src").get()
                
                # Check for trailers
                header_texts = response.xpath("//div[@class='item-center']/text()").getall()
            
                if 'Bandes-annonces' in header_texts:
                    # Click on trailer link
                    try:
                        trailer_link = self.driver.find_element(By.XPATH, "//a[contains(@title, 'Bandes-annonces')]")
                        trailer_link.click()
                        
                        # Handle popup
                        try:
                            self.driver.execute_script("document.getElementById('didomi-popup').style.display='none';")
                        except Exception:
                            pass
                        
                        # Wait for page to load
                        time.sleep(2)
                        
                        # Get current URL
                        trailer_page_url = self.driver.current_url
                        
                        # Follow to parse trailer
                        yield scrapy.Request(
                            url=trailer_page_url,
                            callback=self.parse_trailer,
                            meta={'meta_item': item},
                            dont_filter=True
                        )
                        return
                    except Exception as e:
                        self.logger.error(f"Error clicking trailer link: {e}")
            
                # Check for box office
                if 'Box Office' in header_texts:
                    box_office_url = response.url.replace('_gen_cfilm=', '-').replace('.html', '/box-office/')
                    yield scrapy.Request(
                        url=box_office_url,
                        callback=self.parse_boxoffice,
                        meta={'meta_item': item},
                        dont_filter=True
                    )
                    return
            
        except Exception as e:
            self.logger.error(f"Error in parse_film: {e}")
            
            
            
    def parse_trailer(self, response):
        
        self.logger.info(f"Parsing trailer page: {response.url}")
        
        try:
            item = response.meta['meta_item']
            
            item['trailer_date'] = response.xpath("//div[contains(@class, 'media-info-item') and contains(@class, 'icon-eye')]/text()").get()
            item['trailer_date'] = item['trailer_date'].strip() if item['trailer_date'] else None
            
            item['trailer_number'] = response.css('div.titlebar-title::text').get()
            item['trailer_number'] = item['trailer_number'].strip() if item['trailer_number'] else None
            
            item['trailer_views'] = response.xpath("//div[contains(@class, 'media-info-item') and contains(@class, 'icon-time')]/text()").get()
            item['trailer_views'] = item['trailer_views'].strip() if item['trailer_views'] else None

            # Get trailer URL using Selenium
            try:
                trailer_iframe = self.driver.find_element(By.CSS_SELECTOR, "iframe[src*='dailymotion']")
                if trailer_iframe:
                    iframe_src = trailer_iframe.get_attribute('src')
                    item['trailer_url'] = iframe_src.strip() if iframe_src else None
            except Exception as e:
                self.logger.error(f"Error extracting trailer URL: {e}")
                item['trailer_url'] = None

            # Check for box office data
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
            
            # If no box office data, yield the item
            yield item
            
        except Exception as e:
            self.logger.error(f"Error in parse_trailer: {e}")
            # Yield the item to avoid losing data
            if 'meta_item' in response.meta:
                yield response.meta['meta_item']
                

    def parse_boxoffice(self, response):
        item = response.meta['meta_item']
        
        try:
        
            # Get first week box office
            box_office_fr = response.xpath('//h2[contains(text(), "Box Office France")]/parent::div/following-sibling::table[1]//tr[position() = 1]/td[2]/text()').get()
            item['box_office_fr'] = box_office_fr.strip() if box_office_fr else None
            
            box_office_us = response.xpath('//h2[contains(text(), "Box Office US")]/parent::div/following-sibling::table[1]//tr[position() = 1]/td[2]/text()').get()
            item['box_office_us'] = box_office_us.strip() if box_office_us else None
            
            # Get total box office (last row, third column)
            total_box_office_fr = response.xpath('//h2[contains(text(), "Box Office France")]/parent::div/following-sibling::table[1]//tr[last()]/td[3]/text()').get()
            item['total_box_office_fr'] = total_box_office_fr.strip() if total_box_office_fr else None
            
            total_box_office_us = response.xpath('//h2[contains(text(), "Box Office US")]/parent::div/following-sibling::table[1]//tr[last()]/td[3]/text()').get()
            item['total_box_office_us'] = total_box_office_us.strip() if total_box_office_us else None
        
        except Exception as e:
            self.logger.error(f"Error in parse_boxoffice: {e}")
            # Yield the item to avoid losing data
            if 'meta_item' in response.meta:
                yield response.meta['meta_item']

    def closed(self, reason):
        """Close the browser when the spider is closed."""
        self.logger.info(f"Spider closed: {reason}")
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()
            self.logger.info("Selenium driver closed")