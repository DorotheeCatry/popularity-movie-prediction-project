import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.selector import Selector
import time

class FilmsSeleniumSpider(scrapy.Spider):
    name = "films"

    def start_requests(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.binary_location = "/usr/bin/chromium-browser"

        driver = webdriver.Chrome(options=chrome_options)

        url = "https://www.jpbox-office.com/v9_demarrage.php?view=2"
        driver.get(url)
        time.sleep(5)

        sel = Selector(text=driver.page_source)
        driver.quit()

        # ✅ Sélection correcte des lignes
        rows = sel.xpath('//tr[td[@class="col_poster_titre "]]')
        
        for row in rows:
            try:
                yield {
                    "rang": row.xpath('./td[1]//div/text()').get(default='').strip(),
                    "titre": row.xpath('./td[3]//h3/a/text()').get(default='').strip(),
                    "titre_vo": row.xpath('./td[3]/text()[normalize-space()]').get(default='').strip(),
                    "realisateur": row.xpath('./td[3]//a[2]/text()').get(default='').strip(),
                    "genre": row.xpath('./td[3]//a[last()]/text()').get(default='').strip(),
                    "annee": row.xpath('./td[4]/a/text()').get(default='').strip(),
                    "pays": row.xpath('./td[5]//img/@src').get(default='').split("/")[-1].replace(".jpg", ""),
                    "entrees": row.xpath('./td[6]/text()').get(default='').strip().replace('\u00a0', '').replace(' ', ''),
                    "salles": row.xpath('./td[7]/text()').get(default='').strip().replace('\u00a0', '').replace(' ', ''),
                    "moy_salle": row.xpath('./td[8]/text()').get(default='').strip().replace('\u00a0', '').replace(' ', ''),
                    "part_marche": row.xpath('./td[9]/text()').get(default='').strip(),
                    "affiche": row.xpath('./td[2]/img/@src').get(default='').strip(),
                }
            except Exception as e:
                self.logger.warning(f"Ligne ignorée à cause de : {e}")
