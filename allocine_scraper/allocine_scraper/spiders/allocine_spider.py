import scrapy

class AllocineSpider(scrapy.Spider):
    name = "allocine"
    allowed_domains = ["allocine.fr"]
    start_urls = [f"https://www.allocine.fr/films/?page={i}" for i in range(1, 2)]  # Scrape les 2 premières pages (ajustez selon votre besoin)

    def parse(self, response):
        # On récupère les films sur la page actuelle
        for film in response.css('div.card.entity-card.entity-card-list.cf'):
            # Extraction des informations de base sur chaque film
            titre = film.css("h2.meta-title a::text").get()
            lien = response.urljoin(film.css("h2.meta-title a::attr(href)").get())

            yield {
                "titre": titre,
                "lien": lien,
            }

            # Suivi du lien pour récupérer les détails de chaque film
            yield response.follow(lien, self.parse_movie)

        # Pagination : recherche du lien vers la page suivante et appel de `parse` récursivement
        next_page = response.css("a.button.button-md.button-primary-right::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_movie(self, response):
        """Scrape les détails du film"""
        
        # Fonction pour extraire des informations techniques basées sur le label (par exemple, Langues, Type de film)

        # Extraction des informations détaillées du film
        yield {
            "title": response.css("div.titlebar-title::text").get(),
            "image_url": response.css("figure.thumbnail img.thumbnail-img::attr(src)").get(),
            "release_date": response.css("a.date.blue-link::text").get(),
            "duration": response.css("div.meta-body-info span::text").re_first(r"\d+h \d+min"),
            "genres": response.css("a.dark-grey-link[href*='genre']::text").getall(),
            "director": response.css("div.meta-body-direction a::text").get(),
            "actors": response.css("div.meta-body-actor a::text").getall(),
            "synopsis": response.css("div.content-txt p.bo-p::text").get(),
            "critic_rating": response.css("div.rating-holder a[href*='presse'] + div span.stareval-note::text").get(),
            "viewer_rating": response.css("div.rating-holder a[href*='spectateurs'] + div span.stareval-note::text").get(),
            "countries": response.css("a.nationality::text").getall(),
            "distributor": response.css("a.blue-link[href*='fichesociete']::text").get(),
            "box_office": response.css("a.blue-link[href*='box-office']::text").re_first(r"[\d\s]+"),
            "production_year": response.css("div.item span.that::text").re_first(r"\d{4}"),
        }
