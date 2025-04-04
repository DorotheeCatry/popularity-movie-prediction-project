import scrapy

class FilmDemarrageSpider(scrapy.Spider):
    name = "film_demarrage"
    allowed_domains = ["jpbox-office.com"]
    start_urls = ["https://www.jpbox-office.com/fichfilm.php?id=10042"]

    def parse(self, response):
        budget = response.css('table.tablesmall tr:first-child td:last-child div strong::text').get()
        # Extract "Démarrage"
        demarrage = response.css("td:nth-child(3) table.tablesmall.tablesmall1b tr:nth-child(2) td:nth-child(2) div::text").get()
        if demarrage:
            demarrage = demarrage.strip()

        # Return extracted data
        yield {
            'budget': budget,
            'demarrage': demarrage,
        }
