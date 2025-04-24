import time
import scrapy
import re
from selenium.webdriver.common.by import By
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from allocine_scraper.items import MovieReleaseScraperParsingItem
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.selector import Selector
from allocine_scraper.utils import parse_date, convert_to_minutes

class NewReleaseMovieSpider(CrawlSpider):
    name = "newreleasespider"
    allowed_domains = ["allocine.fr"]
    start_urls = ["https://www.allocine.fr/film/agenda"]
    
    custom_settings = {
        'ITEM_PIPELINES': {
            'allocine_scraper.pipelines.ReleaseDatabasePipeline': 300,
        }
    }

    rules = (
        Rule(LinkExtractor(restrict_xpaths="//a[@class='meta-title-link']"), callback='parse_film', follow=True),
    )

    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = "/usr/bin/chromium-browser"
        
        # Désactiver les pop-ups et publicités
        chrome_options.add_argument("--disable-notifications")  # Désactiver les notifications
        chrome_options.add_argument("--disable-ads")            # Désactiver les publicités
        chrome_options.add_argument("--disable-extensions")     # Désactiver les extensions pour éviter les pubs
        
        self.driver = webdriver.Chrome(options=chrome_options)  # Initialisation du WebDriver Chrome

    def start_requests(self):
        # Envoie la première requête avec Selenium (ChromeDriver)
        self.driver.get(self.start_urls[0])

        # Masquer le pop-up si présent
        try:
            self.driver.execute_script("document.getElementById('didomi-popup').style.display='none';")
        except Exception as e:
            self.logger.warning(f"Erreur lors de la fermeture du pop-up: {e}")

        yield scrapy.Request(
            url=self.driver.current_url,
            callback=self.parse,
        )

    def parse(self, response):
        # Utilisation de Selenium pour récupérer la page source après interaction avec JavaScript
        self.driver.get(response.url)
        
        # Masquer à nouveau le pop-up si nécessaire
        try:
            self.driver.execute_script("document.getElementById('didomi-popup').style.display='none';")
        except Exception as e:
            self.logger.warning(f"Erreur lors de la fermeture du pop-up: {e}")

        # Création d'un sélecteur avec le contenu de la page
        sel = Selector(text=self.driver.page_source)
        
        # Scraper les films (links) sur la page actuelle
        for link in sel.xpath("//a[@class='meta-title-link']/@href").getall():
            yield response.follow(link, callback=self.parse_film)

        try:
            # Recherche du bouton "Suivante" généré par JavaScript
            next_button = self.driver.find_element(By.XPATH, "//a[contains(@class, 'button-right') and .//span[text()='Suivante']]")
            
            # Clique sur le bouton "Suivante"
            next_button.click()
            self.driver.execute_script("document.getElementById('didomi-popup').style.display='none';")

            # Attendre que la page suivante soit complètement chargée
            WebDriverWait(self.driver, 2)

            # Récupérer le nouveau contenu après le clic
            time.sleep(10)  # Temps pour s'assurer que la page a bien chargé
            new_response = scrapy.http.Response(self.driver.current_url, body=self.driver.page_source.encode('utf-8'))
            
            # Vérifier si l'URL a changé et s'il y a un changement dans le contenu
            if new_response.url != response.url:
                yield scrapy.Request(new_response.url, callback=self.parse)  # Relancer `parse` avec la nouvelle page
            else:
                self.logger.warning("Pas de changement d'URL après le clic sur 'Suivante', le scraping semble bloqué.")
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la navigation vers la page suivante : {e}")
            
    def parse_film(self, response):
        
        release_cinema = response.xpath('//*[contains(@class, "date")]/text()').get()
        release_cinema = parse_date(release_cinema)
        
        
        url_date_match = re.search(r'(\d{4}-\d{2}-\d{2})', response.url)
        
        if release_cinema == url_date_match:
        
            item = MovieReleaseScraperParsingItem()

            # Extraction des informations principales
            item['title'] = response.xpath("//div[@class='titlebar-title titlebar-title-xl']/text()").get()
            item['original_title'] = response.xpath('//span[normalize-space(text())="Titre original"]/following-sibling::span/text()').get()
            item['original_title'] = item['original_title'].strip() if item['original_title'] else None

            item['release_date'] = response.xpath('//*[contains(@class, "date")]/text()').get()
            item['release_date'] = item['release_date'].strip() if item['release_date'] else None

            item['duration'] = response.xpath("//div[@class='meta-body-item meta-body-info']//text()[contains(., 'h') and contains(., 'min')]").get()
            item['duration'] = item['duration'].strip() if item['duration'] else None

            item['genres'] = response.xpath("//div[contains(@class, 'meta-body-info')]//span[contains(@class, 'dark-grey-link')]/text()").getall()
            item['genres'] = item['genres'] if item['genres'] else None

            # Ratings
            ratings = response.xpath("//div[@class='stareval stareval-small stareval-theme-default']/span[@class='stareval-note']/text()").getall()
            item['press_rating'] = ratings[0] if len(ratings) > 0 else None
            item['audience_rating'] = ratings[1] if len(ratings) > 1 else None

            item['director'] = response.xpath("//div[@class='meta-body-item meta-body-direction meta-body-oneline']/span[normalize-space(text())='De']/following-sibling::span/text()").getall()
            item['director'] = item['director'] if item['director'] else None

            item['writer'] = response.xpath("//div[@class='meta-body-item meta-body-direction meta-body-oneline']/span[normalize-space(text())='Par']/following-sibling::span/text()").getall()
            item['writer'] = item['writer'] if item['writer'] else None

            item['audience'] = response.xpath("//div[@class='certificate']/span[@class='certificate-text']/text()").get()
            item['audience'] = item['audience'] if item['audience'] else None

            item['distributor'] = response.xpath("//section[@class='section ovw ovw-technical']//span[text()='Distributeur']/following-sibling::span/text()").get()
            item['distributor'] = item['distributor'] if item['distributor'] else None

            item['movie_type'] = response.xpath("//section[@class='section ovw ovw-technical']//span[text()='Type de film']/following-sibling::span/text()").get()
            item['movie_type'] = item['movie_type'] if item['movie_type'] else None

            item['nationality'] = response.css("div.item span.what.light:contains('Nationalité') + span span.nationality::text").getall()
            item['nationality'] = item['nationality'] if item['nationality'] else None

            item['languages'] = response.xpath("//section[@class='section ovw ovw-technical']//span[text()='Langues']/following-sibling::span/text()").getall()
            item['languages'] = [lang.strip() for lang in item['languages']] if item['languages'] else None

            item['synopsis'] = response.xpath("//p[@class='bo-p']/text()").get()
            item['synopsis'] = item['synopsis'] if item['synopsis'] else None

            item['actors'] = response.xpath("//div[contains(@class, 'meta-body-item meta-body-actor')]//span[contains(@class, 'dark-grey-link')]/text()").getall()
            item['actors'] = item['actors'] if item['actors'] else None

            item['image_url'] = response.xpath("//img[@class='thumbnail-img']/@src").get()
            item['image_url'] = item['image_url'] if item['image_url'] else None

            # Vérifier si le film a un onglet "Box Office"
            header = response.xpath("//div[@class='item-center']/text()").getall()
            if 'Box Office' in header:
                casting_url = response.url.replace('_gen_cfilm=', '-').replace('.html', '/box-office/')
                yield scrapy.Request(casting_url, meta={'meta_item': item}, callback=self.parse_boxoffice)
            else:
                yield item

    def parse_boxoffice(self, response):
        item = response.meta['meta_item']
        
        # Extraction des données Box Office
        item['box_office_fr'] = response.xpath('//h2[contains(text(), "Box Office France")]/parent::div/following-sibling::table[1]//tr[position() = 1]/td[2]/text()').get()
        item['box_office_fr'] = item['box_office_fr'].strip() if item['box_office_fr'] else None

        item['box_office_us'] = response.xpath('//h2[contains(text(), "Box Office US")]/parent::div/following-sibling::table[1]//tr[position() = 1]/td[2]/text()').get()
        item['box_office_us'] = item['box_office_us'].strip() if item['box_office_us'] else None

        yield item