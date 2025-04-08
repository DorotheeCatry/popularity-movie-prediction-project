from pathlib import Path

import scrapy
import re


class AllocineSpider(scrapy.Spider):
    name = "allocinespider"

    allowed_domains = ["allocine.fr"]

    start_urls = ["https://www.allocine.fr/films/decennie-2010/?page=" + str(x) for x in range(1, 3)]


    def parse(self, response):
        movie_links = response.css('div.entity-card-list div.meta-affintiy-score h2.meta-title a.meta-title-link::attr(href)').getall()
        movie_links_clean = ["https://www.allocine.fr" + link for link in movie_links]
        
        # Pour chaque lien, on appelle parse_movie
        for link in movie_links_clean:
            yield response.follow(link, callback=self.parse_movie)


    def parse_movie(self, response):
        title = response.css('div.titlebar-title::text').get()

        image = response.css('div.entity-card-player-ovw figure.thumbnail span.thumbnail-container img').attrib["src"]

        date = response.css('div.entity-card-player-ovw div.meta div.meta-body div.meta-body-item span.date::text').get().replace('\n', ' ').strip()

        broadcast_place = response.css('div.entity-card-player-ovw div.meta div.meta-body div.meta-body-info span.meta-release-type::text').get().replace('\n', ' ').strip()

        genres = response.css('div.entity-card-player-ovw div.meta div.meta-body div.meta-body-info span.dark-grey-link::text').getall()

        certificate = response.css("section.ovw-synopsis div.certificate span.certificate-text::text").get()
        certificate_clean = str(certificate.replace('\n', ' ').strip()) if certificate != None else "Tout public"

        synopsis = response.css("section.ovw-synopsis div.content-txt p.bo-p::text").getall()
        synopsis_clean = []
        for paragraph in synopsis:
            clean_paragraph = paragraph.replace('\n', ' ').strip()
            clean_paragraph = clean_paragraph.replace("'","\'" )
            synopsis_clean.append(clean_paragraph)

        directors_filter = response.css('div.entity-card-player-ovw div.meta div.meta-body div.meta-body-direction')[0]
        directors = directors_filter.css('span.dark-grey-link::text').getall()
        directors_clean = [str(director) for director in directors]

        scenarists_filter = response.css('div.entity-card-player-ovw div.meta div.meta-body div.meta-body-direction')[1]
        scenarists = scenarists_filter.css('span.dark-grey-link::text').getall()
        scenarists_clean = [str(scenarist) for scenarist in scenarists]

        actors = response.css('div.entity-card-player-ovw div.meta div.meta-body div.meta-body-actor span.dark-grey-link::text').getall()
        actors_clean = [str(actor) for actor in actors]

        average_notes_press = response.css("div.entity-card-player-ovw div.rating-holder div.rating-item div.rating-item-content div.stareval-theme-default span.stareval-note::text").get()
        average_notes_spectators = response.css("div.entity-card-player-ovw div.rating-holder div.rating-item div.rating-item-content div.stareval-theme-default span.stareval-note::text")[1].get()

        nationality = response.css("section.ovw-technical div.item span.that span.nationality::text").getall()
        nationality_clean = [str(country.strip()) for country in nationality]

        distributor = response.css("section.ovw-technical div.item span.blue-link::text").get().strip()

        awards = response.css("section.ovw-technical div.item span.blue-link::text")[1].get().replace('\n', ' ').strip()
        awards_clean = str(awards)

        year_production = response.css("section.ovw-technical div.item span.that::text")[4].get()

        movie_type = response.css("section.ovw-technical div.item span.that::text")[8].get().strip()
        language = response.css("section.ovw-technical div.item span.that::text")[12].get().replace('\n', ' ').strip()

        # target
        entrance_number_fr = response.css("section.ovw-technical div.item span.blue-link::text")[2].get().replace('\n', ' ').strip()

        yield {
            'title': str(title),
            'image': str(image),
            'date': str(date),
            'broadcast_place': str(broadcast_place),
            'genres': genres,
            'certificate': str(certificate_clean),
            'synopsis': synopsis_clean,
            'directors': directors_clean,
            'scenarists': scenarists,
            'actors': actors,
            'average_notes_press': float(average_notes_press),
            'average_notes_spectators': float(average_notes_spectators),
            'nationality': nationality_clean,
            'distributor': str(distributor),
            'awards': awards_clean,
            'year_production': int(year_production),
            'movie_type': str(movie_type),
            'language': str(language),
            'entrance_number_fr': str(entrance_number_fr),
        }




