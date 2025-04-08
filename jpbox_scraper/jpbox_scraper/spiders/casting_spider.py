import scrapy
import re

class CastingSpider(scrapy.Spider):
    name = "casting"
    start_urls = []

    custom_settings = {
        "FEEDS": {
            "casting_detail.csv": {
                "format": "csv",
                "encoding": "utf8",
                "overwrite": True
            }
        },
        "FEED_EXPORT_FIELDS": [
            "film_id", "person_id", "nom_personne", "role", "personnage",
            "photo_path", "nb_films", "cumul_FR", "moyenne_FR", "cumul_US"
        ]
    }

    def start_requests(self):
        # Replace with your actual list of film_ids
        film_ids = [1, 2, 3]  # example IDs
        for film_id in film_ids:
            url = f"https://www.jpbox-office.com/fichfilm.php?id={film_id}&view=7"
            yield scrapy.Request(url, callback=self.parse_casting, meta={'film_id': film_id})

    def parse_casting(self, response):
        film_id = response.meta['film_id']
        current_section = None

        for row in response.xpath('//table[@class="tablesmall tablesmall5"]//tr'):
            section = row.xpath('.//td[@class="celluletitre"]/text()').get()
            if section:
                current_section = section.strip()
                continue

            person_link = row.xpath('.//td[@class="col_poster_titre"]//a[contains(@href, "fichacteur.php")]/@href').get()
            if person_link:
                person_id_match = re.search(r'id=(\d+)', person_link)
                if person_id_match:
                    person_id = person_id_match.group(1)
                    nom = row.xpath('.//td[@class="col_poster_titre"]//a/text()').get(default='').strip()
                    personnage = ' '.join(row.xpath('.//td[@class="col_poster_titre"][2]/text()').getall()).strip()
                    personnage = personnage.replace('\xa0', ' ').strip()

                    # Go to person profile page
                    url = f"https://www.jpbox-office.com/fichacteur.php?id={person_id}"
                    yield scrapy.Request(
                        url,
                        callback=self.parse_person_profile,
                        meta={
                            'film_id': film_id,
                            'person_id': person_id,
                            'nom_personne': nom,
                            'role': current_section,
                            'personnage': personnage
                        }
                    )

    def parse_person_profile(self, response):
        data = response.meta

        photo_path = response.xpath('//td[@class="blocgauche_2022titre_image"]/img/@src').get(default='').strip()

        cumul_FR = response.xpath('//caption[contains(text(), "ENTREES FRANCE")]/following-sibling::tr[1]/td[2]//text()').get(default='').strip()
        moyenne_FR = response.xpath('//caption[contains(text(), "ENTREES FRANCE")]/following-sibling::tr[2]/td[2]//text()').get(default='').strip()
        nb_films = response.xpath('//a[contains(@href, "&view=7")]/text()').re_first(r'(\d+) films')
        cumul_US = response.xpath('//caption[contains(text(), "RECETTES")]/following-sibling::tr[1]/td[2]//text()').get(default='').strip()

        yield {
            "film_id": data["film_id"],
            "person_id": data["person_id"],
            "nom_personne": data["nom_personne"],
            "role": data["role"],
            "personnage": data["personnage"],
            "photo_path": photo_path,
            "nb_films": nb_films,
            "cumul_FR": cumul_FR.replace('\xa0', '').replace(' ', '').replace('$', ''),
            "moyenne_FR": moyenne_FR.replace('\xa0', '').replace(' ', '').replace('$', ''),
            "cumul_US": cumul_US.replace('\xa0', '').replace(' ', '').replace('$', '')
        }
