import scrapy
from datetime import datetime, timedelta
from allohebdo.items import FilmItem
from allohebdo.utils import parse_french_date


class AgendaNextWedSpider(scrapy.Spider):
    name = "agenda_nextwed"
    allowed_domains = ["allocine.fr"]
    start_urls = ["https://www.allocine.fr/film/agenda/"]

    # -----------------------------------------------------------
    def parse(self, response):
        # date limite = mercredi prochain
        today = datetime.utcnow().date()
        days_to_wed = (2 - today.weekday()) % 7 or 7
        next_wed = today + timedelta(days=days_to_wed)

        for card in response.css("li.mdl div.card.entity-card"):
            date_str = card.css(".meta-body-info .date::text").get()
            if not date_str:
                continue
            date_dt = parse_french_date(date_str)
            if not date_dt or date_dt.date() > next_wed:
                continue

            item = FilmItem(
                title        = card.css(".meta-title-link::text").get("").strip(),
                release_date = date_dt.date().isoformat(),
                genres       = [g.get().strip() for g in card.css(".meta-body-info a::text")],
                director     = card.css(".meta-body-direction a::text").get(default="").strip(),
                actors       = [a.get().strip() for a in card.css(".meta-body-actor a::text")],
                synopsis     = " ".join(card.css(".synopsis .content-txt::text").getall()).strip(),
                sessions     = card.css(".buttons-holder a::text").re_first(r"(\d+)") or "0",
            )

            url_film = response.urljoin(card.css(".meta-title-link::attr(href)").get())
            yield response.follow(url_film, self.parse_film, cb_kwargs={"item": item})

    # -----------------------------------------------------------
    def parse_film(self, response, item: FilmItem):
        item["duration"] = response.css(".meta-body-info::text").re_first(r"\d+h\s*\d*min") or ""

        cast_link = response.css('a[title*="Casting complet"]::attr(href)').get()
        if cast_link:
            yield response.follow(
                response.urljoin(cast_link),
                self.parse_casting,
                cb_kwargs={"item": item},
            )
        else:
            # champs optionnels par défaut
            item["writer"]        = None
            item["producers"]     = []
            item["distributor"]   = None
            item["trailer_views"] = 0
            yield item

    # -----------------------------------------------------------
    def parse_casting(self, response, item: FilmItem):
        item["writer"] = response.xpath(
            '//a[contains(@title,"Scénariste")]/following-sibling::span/text()'
        ).get(default="").strip() or None

        item["producers"] = [
            p.strip()
            for p in response.xpath('//div[h2[contains(text(),"Production")]]/div/a/text()').getall()
        ]

        item["distributor"] = response.xpath(
            '//div[h2[contains(text(),"Sociétés")]]'
            '/div[span[contains(@class,"light") and contains(text(),"Distribution")]]'
            '/span[@class="item"]/text()'
        ).get(default="").strip() or None

        trailer_rel = response.css('a[href*="player_gen_cmedia"]::attr(href)').get()
        if trailer_rel:
            yield response.follow(
                response.urljoin(trailer_rel),
                self.parse_trailer,
                cb_kwargs={"item": item},
            )
        else:
            item["trailer_views"] = 0
            yield item

    # -----------------------------------------------------------
    def parse_trailer(self, response, item: FilmItem):
        vues_txt = response.css(".media-info-item.icon-eye::text").get(default="0")
        item["trailer_views"] = int("".join(c for c in vues_txt if c.isdigit()) or 0)
        yield item




