import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.selector import Selector
import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from statistics import mean

class FilmsSeleniumSpider(scrapy.Spider):
    name = "films"
    custom_settings = {
        "DUPEFILTER_DEBUG": True,
        "FEED_EXPORT_ENCODING": "utf-8",
        "DUPEFILTER_CLASS": "scrapy.dupefilters.BaseDupeFilter",  # Disable duplicate filtering
        "FEED_EXPORT_FIELDS": [
            "film_id", "realisateur_id", "rang", "titre", "titre_vo",
            "realisateur", "genre", "annee", "pays", "entrees", "salles",
            "moy_salle", "part_marche", "affiche", "moyenne_fr_realisateur",
            "sortie", "distributeur", "classification", "acteurs", "moyenne_fr_acteurs"
        ]
    }

    def start_requests(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.binary_location = "/usr/bin/chromium-browser"

        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            url = "https://www.jpbox-office.com/v9_demarrage.php?view=2"
            driver.get(url)

            max_retries = 5
            for attempt in range(max_retries):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "col_poster_titre"))
                )
                
                sel = Selector(text=driver.page_source)
                rows = sel.xpath('//tr[td[contains(@class, "col_poster_titre")] and .//h3/a]')
                
                if len(rows) >= 30:
                    break
                    
                self.logger.info(f"Attempt {attempt + 1}/{max_retries}: Found {len(rows)} rows, expecting 30. Retrying...")
            
            self.logger.info(f"✅ Final row count: {len(rows)}")

            for idx, row in enumerate(rows, 1):
                try:
                    titre = row.xpath('.//h3/a/text()').get(default='').strip()
                    film_href = row.xpath('.//h3/a/@href').get(default='')
                    
                    if not titre or not film_href:
                        self.logger.error(f"Row {idx}: Missing title or href for content: {row.get()}")
                        continue
                        
                    match = re.search(r'id=(\d+)', film_href)
                    film_id = match.group(1) if match else ""
                    
                    if not film_id:
                        self.logger.error(f"Row {idx}: Could not extract film ID from {film_href}")
                        continue

                    realisateur_link = row.xpath('.//a[contains(@href, "fichacteur.php")]/@href').get()
                    realisateur_id_match = re.search(r'id=(\d+)', realisateur_link) if realisateur_link else None
                    realisateur_id = str(realisateur_id_match.group(1)) if realisateur_id_match else ""

                    titre_vo, realisateur, genre = self.extract_details(row)

                    film_data = {
                        "film_id": film_id,
                        "realisateur_id": realisateur_id,
                        "rang": row.xpath('.//td[1]//div/text()').get(default='').strip(),
                        "titre": titre,
                        "titre_vo": titre_vo,
                        "realisateur": realisateur,
                        "genre": genre,
                        "annee": row.xpath('.//td[4]/a/text()').get(default='').strip(),
                        "pays": row.xpath('.//td[5]//img/@src').get(default='').split("/")[-1].replace(".jpg", ""),
                        "entrees": row.xpath('.//td[6]/text()').get(default='').strip().replace('\u00a0', '').replace(' ', ''),
                        "salles": row.xpath('.//td[7]/text()').get(default='').strip().replace('\u00a0', '').replace(' ', ''),
                        "moy_salle": row.xpath('.//td[8]/text()').get(default='').strip().replace('\u00a0', '').replace(' ', ''),
                        "part_marche": row.xpath('.//td[9]/text()').get(default='').strip(),
                        "affiche": row.xpath('.//td[2]/img/@src').get(default='').strip(),
                        "acteurs": [],
                        "moyenne_fr_acteurs": ""
                    }

                    self.logger.info(f"Processing film {idx}: {titre} (ID: {film_id})")

                    cast_url = f"https://www.jpbox-office.com/fichfilm.php?id={film_id}&view=7"
                    yield scrapy.Request(
                        cast_url,
                        callback=self.parse_cast,
                        meta={'film': film_data},
                        errback=self.handle_error,
                        dont_filter=True
                    )

                except Exception as e:
                    self.logger.error(f"Error processing row {idx}: {str(e)}")
                    continue

        finally:
            driver.quit()

    def extract_details(self, row):
        try:
            titre_vo, realisateur, genre = "", "", ""

            a_tags = row.xpath('.//td[3]//a')
            a_texts = [a.xpath('text()').get(default='').strip() for a in a_tags]
            a_hrefs = [a.xpath('@href').get(default='') for a in a_tags]

            full_texts = row.xpath('.//td[3]//text()').getall()
            full_texts_clean = [t.strip() for t in full_texts if t.strip()]

            for i, t in enumerate(full_texts_clean):
                if "Réalisé par" in t and i > 0:
                    titre_vo = full_texts_clean[i - 1].strip()
                    break

            for href, text in zip(a_hrefs, a_texts):
                if "fichacteur.php" in href:
                    realisateur = text
                elif "filtre=genre" in href:
                    genre = text

            return titre_vo, realisateur, genre
        except Exception as e:
            self.logger.error(f"Error in extract_details: {str(e)}")
            return "", "", ""

    def parse_cast(self, response):
        film = response.meta['film']
        try:
            # Find the table containing the casting information
            cast_table = response.xpath('//table[@class="tablesmall tablesmall5"]')
            if not cast_table:
                return self.proceed_with_director(response, film)

            actor_data = []
            in_actors_section = False

            # Iterate through all rows in the table
            for row in cast_table.xpath('.//tr'):
                # Check for section headers
                section_header = row.xpath('.//td[@class="celluletitre"]/text()').get()
                if section_header:
                    section_header = section_header.strip()
                    if section_header == "Acteurs et actrices":
                        in_actors_section = True
                        continue
                    elif in_actors_section:  # If we were in actors section and hit a new section
                        break  # Stop processing as we've left the actors section

                # Only process rows when we're in the actors section
                if in_actors_section:
                    # Get actor information if the row contains an actor
                    actor_link = row.xpath('.//td[@class="col_poster_titre"]//a[contains(@href, "fichacteur.php")]/@href').get()
                    if actor_link:
                        # Only process if the role type indicates it's an actor (not a producer, writer, etc.)
                        role_type = row.xpath('.//td[@class="col_poster_titre"][2]/i/text()').get('')
                        if any(keyword in role_type for keyword in ['Rôle principal', 'Second rôle', 'Apparition', 'Voix-off']):
                            actor_name = row.xpath('.//td[@class="col_poster_titre"]//a/text()').get('').strip()
                            character_name = row.xpath('.//td[@class="col_poster_titre"][2]/text()').getall()
                            character_name = ' '.join([r.strip() for r in character_name if r.strip()])
                            
                            # Extract actor ID from the link
                            actor_id_match = re.search(r'id=(\d+)', actor_link)
                            if actor_id_match:
                                actor_id = actor_id_match.group(1)
                                actor_data.append({
                                    'id': actor_id,
                                    'name': actor_name,
                                    'role': role_type,
                                    'character': character_name
                                })

            film['acteurs'] = actor_data
            
            if actor_data:
                return self.fetch_actor_averages(response, film, actor_data)
            else:
                return self.proceed_with_director(response, film)

        except Exception as e:
            self.logger.error(f"Error in parse_cast for {film['titre']}: {str(e)}")
            return self.proceed_with_director(response, film)

    def fetch_actor_averages(self, response, film, actors):
        try:
            film['actor_data'] = {'total': len(actors), 'processed': 0, 'averages': []}
            actor = actors[0]
            url = f"https://www.jpbox-office.com/fichacteur.php?id={actor['id']}"
            return scrapy.Request(
                url,
                callback=self.parse_actor_average,
                meta={'film': film, 'actor_index': 0},
                errback=self.handle_error,
                dont_filter=True
            )
        except Exception as e:
            self.logger.error(f"Error in fetch_actor_averages: {str(e)}")
            return self.proceed_with_director(response, film)

    def parse_actor_average(self, response):
        film = response.meta['film']
        actor_index = response.meta['actor_index']
        
        try:
            france_table = response.xpath('//caption[contains(text(), "ENTREES FRANCE")]/parent::table')
            moyenne = france_table.xpath('.//tr[td[contains(text(), "Moyenne")]]/td[2]//text()').get()
            if moyenne:
                moyenne = int(moyenne.strip().replace('\u00a0', '').replace(' ', ''))
                film['actor_data']['averages'].append(moyenne)
            
            film['actor_data']['processed'] += 1
            
            if film['actor_data']['processed'] >= film['actor_data']['total']:
                if film['actor_data']['averages']:
                    film['moyenne_fr_acteurs'] = str(int(mean(film['actor_data']['averages'])))
                    self.logger.info(f"🎭 Actors moyenne for {film['titre']} → {film['moyenne_fr_acteurs']}")
                del film['actor_data']
                return self.proceed_with_director(response, film)
            else:
                next_actor = film['acteurs'][actor_index + 1]
                url = f"https://www.jpbox-office.com/fichacteur.php?id={next_actor['id']}"
                return scrapy.Request(
                    url,
                    callback=self.parse_actor_average,
                    meta={'film': film, 'actor_index': actor_index + 1},
                    errback=self.handle_error,
                    dont_filter=True
                )
        except Exception as e:
            self.logger.error(f"Error in parse_actor_average: {str(e)}")
            return self.proceed_with_director(response, film)

    def proceed_with_director(self, response, film):
        if film['realisateur_id']:
            url = f"https://www.jpbox-office.com/fichacteur.php?id={film['realisateur_id']}"
            return scrapy.Request(
                url,
                callback=self.parse_realisateur,
                meta={'film': film},
                errback=self.handle_error,
                dont_filter=True
            )
        else:
            film["moyenne_fr_realisateur"] = ""
            url = f"https://www.jpbox-office.com/fichfilm.php?id={film['film_id']}&view=2"
            return scrapy.Request(
                url,
                callback=self.parse_detail,
                meta={'film': film},
                errback=self.handle_error,
                dont_filter=True
            )

    def parse_realisateur(self, response):
        film = response.meta['film']
        try:
            france_table = response.xpath('//caption[contains(text(), "ENTREES FRANCE")]/parent::table')
            moyenne = france_table.xpath('.//tr[td[contains(text(), "Moyenne")]]/td[2]//text()').get()
            if moyenne:
                moyenne = moyenne.strip().replace('\u00a0', '').replace(' ', '')
            else:
                moyenne = ""
            film["moyenne_fr_realisateur"] = moyenne
            self.logger.info(f"🎬 Realisateur moyenne for {film['titre']} → {moyenne}")
            yield scrapy.Request(
                f"https://www.jpbox-office.com/fichfilm.php?id={film['film_id']}&view=2",
                callback=self.parse_detail,
                meta={'film': film},
                errback=self.handle_error,
                dont_filter=True
            )
        except Exception as e:
            self.logger.error(f"Error in parse_realisateur for {film['titre']}: {str(e)}")
            yield film

    def parse_detail(self, response):
        film = response.meta['film']
        try:
            film["sortie"] = response.xpath('//p[contains(text(), "Sortie")]/a/text()').get(default='').strip()
            film["distributeur"] = response.xpath('//h3[text()="Distribué par"]/following-sibling::text()[1]').get(default='').strip()
            film["classification"] = response.xpath('//div[contains(text(), "public")]/text()').get(default='').strip()
        except Exception as e:
            self.logger.error(f"Error in parse_detail for {film['titre']}: {str(e)}")
        finally:
            yield film

    def handle_error(self, failure):
        self.logger.error(f"Request failed: {failure.value}")
        if 'film' in failure.request.meta:
            yield failure.request.meta['film']