import scrapy
import time
import re

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from allocine_scraper.items import AllocineScraperParsingItem

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


class AllocineSpider(CrawlSpider):
    name = "allocinespider"
    allowed_domains = ["allocine.fr"]
    start_urls = [f"https://allocine.fr/films/?page={x}" for x in range(1, 2000)]

    custom_settings = {
        'ITEM_PIPELINES': {
            "allocine_scraper.pipelines.AllocineDatabasePipeline": 300
        },
        'JOBDIR': 'crawls/allocinespider',
    }

    rules = (
        Rule(LinkExtractor(restrict_xpaths=".//a[@class='meta-title-link']"), callback='parse_film', follow=False),
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
            self.logger.error(f"Error initializing Chrome with binary location: {e}")
            chrome_options.binary_location = ""
            self.driver = webdriver.Chrome(options=chrome_options)

        self.logger.info("Chrome WebDriver initialized successfully.")

    def parse_film(self, response):
        film_url = response.url
        self.logger.info(f"Parsing film: {film_url}")

        try:
            self.driver.get(film_url)
            try:
                self.driver.execute_script("document.getElementById('didomi-popup').style.display='none';")
            except Exception:
                pass

            time.sleep(2)

            item = AllocineScraperParsingItem()

            header = response.xpath("//div[@class='item-center']/text()").getall()

            if any('Box Office' in h for h in header):
                # Informations de base
                item['title'] = response.xpath("//div[@class='titlebar-title titlebar-title-xl']/text()").get()
                self.logger.info(f"Processing movie: {item['title']}")

                item['original_title'] = response.xpath('//span[normalize-space(text())="Titre original"]/following-sibling::span/text()').get()
                if item['original_title']:
                    item['original_title'] = item['original_title'].strip()

                item['release_date'] = response.xpath('//*[contains(@class, "date")]/text()').get()
                if item['release_date']:
                    item['release_date'] = item['release_date'].strip()

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
                if item['audience']:
                    item['audience'] = item['audience'].strip()

                item['distributor'] = response.xpath("//section[@class='section ovw ovw-technical']//span[text()='Distributeur']/following-sibling::span/text()").get()
                if item['distributor']:
                    item['distributor'] = item['distributor'].strip()

                item['movie_type'] = response.xpath("//section[@class='section ovw ovw-technical']//span[text()='Type de film']/following-sibling::span/text()").get()
                if item['movie_type']:
                    item['movie_type'] = item['movie_type'].strip()

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

                # Passage vers la page box office
                box_office_url = response.url.replace('_gen_cfilm=', '-').replace('.html', '/box-office/')
                yield scrapy.Request(
                    url=box_office_url,
                    callback=self.parse_boxoffice,
                    meta={'meta_item': item},
                    dont_filter=True
                )
        
        except Exception as e:
            self.logger.error(f"Error in parse_film: {e}")

    def parse_boxoffice(self, response):
        item = response.meta['meta_item']

        try:
            item['box_office_fr'] = response.xpath('//h2[contains(text(), "Box Office France")]/parent::div/following-sibling::table[1]//tr[1]/td[2]/text()').get()
            if item['box_office_fr']:
                item['box_office_fr'] = item['box_office_fr'].strip()

            item['box_office_us'] = response.xpath('//h2[contains(text(), "Box Office US")]/parent::div/following-sibling::table[1]//tr[1]/td[2]/text()').get()
            if item['box_office_us']:
                item['box_office_us'] = item['box_office_us'].strip()

            item['total_box_office_fr'] = response.xpath('//h2[contains(text(), "Box Office France")]/parent::div/following-sibling::table[1]//tr[last()]/td[3]/text()').get()
            if item['total_box_office_fr']:
                item['total_box_office_fr'] = item['total_box_office_fr'].strip()

            item['total_box_office_us'] = response.xpath('//h2[contains(text(), "Box Office US")]/parent::div/following-sibling::table[1]//tr[last()]/td[3]/text()').get()
            if item['total_box_office_us']:
                item['total_box_office_us'] = item['total_box_office_us'].strip()

            header = response.xpath("//div[@class='item-center']/text()").getall()
            if any('Bandes-annonces' in h for h in header):
                try:
                    trailer_link = self.driver.find_element(By.XPATH, "//a[contains(@title, 'Bandes-annonces')]")
                    trailer_link.click()
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
            
            yield item

        except Exception as e:
            self.logger.error(f"Error in parse_boxoffice: {e}")
            yield item

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
                
            # Get trailer URL
            try:
                trailer_iframe = self.driver.find_element(By.XPATH, "//iframe[contains(@src, 'dailymotion')]").get_attribute('src')

                if trailer_iframe:
                    iframe_src = trailer_iframe.get_attribute('src')
                    trailer_url_match = re.search(r'(?P<url>https?://[^\s"\']+)', iframe_src)
                    if trailer_url_match:
                        item['trailer_url'] = trailer_url_match.group("url").strip()
                    else:
                        item['trailer_url'] = None
                        
            except Exception as e:
                self.logger.error(f"Error extracting trailer URL: {e}")
                item['trailer_url'] = None

            yield item

        except Exception as e:
            self.logger.error(f"Error in parse_trailer: {e}")
            if 'meta_item' in response.meta:
                yield response.meta['meta_item']

    def closed(self, reason):
        self.logger.info(f"Spider closed: {reason}")
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()
            self.logger.info("Selenium driver closed.")
