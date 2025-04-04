import scrapy
from cinescraping.items import CinescrapingItem

class CinespiderSpider(scrapy.Spider):
    name = "cinespider"
    allowed_domains = ["jpbox-office.com"]
    start_urls = ["https://www.jpbox-office.com/v9_demarrage.php?view=2"]

    def parse(self, response):
        # Récupération de tous les films sur la page
        movies = response.css("td.col_poster_titre")

        # extraction des informations pour chaque film
        for movie in movies:
            item = CinescrapingItem()  # Crée un nouvel item pour chaque film
            item["title"] = movie.css('h3 a::text').get()
            item["url_movie"] = movie.css('h3 a').attrib["href"]
            item["realisator"] = movie.css("a::text").getall()[1]
            #item["actors"] = movie.css()
            
            yield item  # Retourne l'item au pipeline ou pour l'exportation

        # # Gestion de la pagination
        # next_page = response.css("div.pagination a:last-child::attr(href)").get()
        # if next_page is not None:
        #     next_page_url = response.urljoin(next_page)  # Crée une URL complète
        #     yield response.follow(next_page_url, callback=self.parse)

          


# recuperation des films par page
#titre_film = response.css('h3 a::text').getall()

#passer la page suivante
#next_page = response.css("div.pagination a:last-child::attr(href)").get()


#recuperation du demarrage sur la page film
demarrage = response.css("td:nth-child(3) table.tablesmall.tablesmall1b tr:nth-child(2) td:nth-child(2) div::text").get()
print(demarrage.strip())

