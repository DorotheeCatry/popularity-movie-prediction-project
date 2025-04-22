# trailer/spiders/trailerspider.py

import scrapy
import re
from datetime import date, datetime, timedelta
from scrapy_playwright.page import PageMethod
from trailer.items import TrailerItem

class TrailerspiderSpider(scrapy.Spider):
    name            = "trailerspider"
    allowed_domains = ["allocine.fr"]
    start_urls      = ["https://www.allocine.fr/video/bandes-annonces/prochainement/"]

    # mappings mois abrégé et complet
    MONTHS = {
        **{"janv.":"01","févr.":"02","mars":"03","avr.":"04",
           "mai":"05","juin":"06","juil.":"07","août":"08",
           "sept.":"09","oct.":"10","nov.":"11","déc.":"12"},
        **{"janvier":"01","février":"02","mars":"03","avril":"04",
           "mai":"05","juin":"06","juillet":"07","août":"08",
           "septembre":"09","octobre":"10","novembre":"11","décembre":"12"}
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={"playwright": True},
                callback=self.parse_list
            )

    def parse_list(self, response):
        # pour chaque vignette, on suit le lien vers la page détail
        for href in response.css(
            "div.card.video-card-trailer a.layer-link::attr(href)"
        ).getall():
            yield scrapy.Request(
                response.urljoin(href),
                meta={
                    "playwright": True,
                    # on attend le rendu de la fiche film
                    "playwright_page_coroutines": [
                        PageMethod("wait_for_selector", "div.media-info-entity")
                    ],
                },
                callback=self.parse_detail
            )

    def parse_detail(self, response):
        # titre et stats vidéo
        titre    = response.css("div.media-info-title::text").get().strip()
        vues_txt = response.css("div.media-info-item.icon-eye::text").get()
        vues     = self.parse_int(vues_txt)

        # date de sortie du film (pas la date du teaser)
        date_txt = response.css(
            "div.media-info-entity .media-info-date a.date::text"
        ).get()
        try:
            ds = self.parse_date_fr(date_txt)
        except ValueError:
            return

        # on ne garde que ceux qui sortent le mercredi suivant
        if vues is not None and ds == self.get_next_wednesday():
            yield TrailerItem(
                titre       = titre,
                vues        = vues,
                date_sortie = ds.isoformat()
            )

    def parse_int(self, txt):
        txt = (txt or "").replace("\u202f", "")
        digits = re.sub(r"[^\d]", "", txt)
        return int(digits) if digits else None

    def parse_date_fr(self, txt):
        s = (txt or "").strip().lower().replace("\u202f", " ")
        for name, num in self.MONTHS.items():
            if name in s:
                day, year = re.sub(name, "", s).split()
                return datetime.strptime(f"{day}-{num}-{year}", "%d-%m-%Y").date()
        raise ValueError(f"Date non reconnue : {txt!r}")

    def get_next_wednesday(self):
        today = date.today()
        delta = (2 - today.weekday()) % 7 or 7
        return today + timedelta(days=delta)

