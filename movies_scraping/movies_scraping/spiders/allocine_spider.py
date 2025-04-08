from pathlib import Path

import scrapy
import re


class AllocineSpider(scrapy.Spider):
    name = "allocinespider"

    allowed_domains = ["allocine.fr"]

    start_urls = ["https://www.allocine.fr/films/decennie-2010/?page=" + str(x) for x in range(1, 1760)]


    def parse(self, response):
        movie_links = response.css('div.entity-card-list div.meta-affintiy-score h2.meta-title a.meta-title-link::attr(href)').getall()
        movie_links_clean = ["https://www.allocine.fr" + link for link in movie_links]
        
        # Pour chaque lien, on appelle parse_movie
        for link in movie_links_clean:
            yield response.follow(link, callback=self.parse_movie)


    def parse_movie(self, response):
        title = response.css('div.titlebar-title::text').get()
        title_clean = str(title)

        image = response.css('div.entity-card-player-ovw figure.thumbnail span.thumbnail-container img').attrib["src"]
        image_clean = str(image)

        date = response.css('div.entity-card-player-ovw div.meta div.meta-body div.meta-body-item span.date::text').get().replace('\n', ' ').strip()
        date_clean = str(date)

        broadcast_place = response.css('div.entity-card-player-ovw div.meta div.meta-body div.meta-body-info span.meta-release-type::text').get().replace('\n', ' ').strip()
        broadcast_place_clean = str(broadcast_place)

        genres = response.css('div.entity-card-player-ovw div.meta div.meta-body div.meta-body-info span.dark-grey-link::text').getall()
        genres_clean = [str(genre) for genre in genres]

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

        # filtrage du nombre d'items 
        technical_infos = response.css("section.ovw-technical div.item").getall()

        if len(technical_infos) == 16:
            nationality = response.css("section.ovw-technical div.item span.that span.nationality::text").getall()
            nationality_clean = [str(country.strip()) for country in nationality]

            distributor = response.css("section.ovw-technical div.item span.blue-link::text").get()
            distributor_clean = str(distributor).strip()

            awards_clean = "Aucun"

            year_production = response.css("section.ovw-technical div.item span.that::text")[4].get()
            year_production_clean = int(year_production)

            movie_type = response.css("section.ovw-technical div.item span.that::text")[8].get()
            movie_type_clean = str(movie_type).strip()

            languages = response.css("section.ovw-technical div.item span.that::text")[12].getall()
            languages_clean = [str(language.replace('\n', '')).strip() for language in languages] if len(languages) > 1 else str(languages[0].replace('\n', '')).strip()

            entrance_number_fr = response.css("section.ovw-technical div.item span.that::text")[10].get()
            entrance_number_fr_clean = str(entrance_number_fr).replace('\n', ' ').strip()

        elif len(technical_infos) == 18:
            nationality = response.css("section.ovw-technical div.item span.that span.nationality::text").getall()
            nationality_clean = [str(country.strip()) for country in nationality]

            distributor = response.css("section.ovw-technical div.item span.blue-link::text").get()
            distributor_clean = str(distributor).strip()

            awards = response.css("section.ovw-technical div.item span.blue-link::text")[1].get()
            awards_clean = str(awards.replace('\n', ' ').strip()) if awards != None else "None"

            year_production = response.css("section.ovw-technical div.item span.that::text")[4].get()
            year_production_clean = int(year_production)

            movie_type = response.css("section.ovw-technical div.item span.that::text")[8].get()
            movie_type_clean = str(movie_type).strip()

            languages = response.css("section.ovw-technical div.item span.that::text")[13].getall()
            languages_clean = [str(language.replace('\n', '')).strip() for language in languages] if len(languages) > 1 else str(languages[0].replace('\n', '')).strip()

            entrance_number_fr = response.css("section.ovw-technical div.item span.blue-link::text")[2].get()
            entrance_number_fr_clean = str(entrance_number_fr).replace('\n', ' ').strip()

        else:
            nationality = response.css("section.ovw-technical div.item span.that span.nationality::text").getall()
            nationality_clean = [str(country.strip()) for country in nationality]

            distributor = response.css("section.ovw-technical div.item span.blue-link::text").get()
            distributor_clean = str(distributor).strip()

            awards = response.css("section.ovw-technical div.item span.blue-link::text")[1].get()
            awards_clean = str(awards.replace('\n', ' ').strip()) if awards != None else "None"

            year_production = response.css("section.ovw-technical div.item span.that::text")[4].get()
            year_production_clean = int(year_production)

            movie_type = response.css("section.ovw-technical div.item span.that::text")[8].get()
            movie_type_clean = str(movie_type).strip()

            languages = response.css("section.ovw-technical div.item span.that::text")[12].getall()
            languages_clean = [str(language.replace('\n', '')).strip() for language in languages] if len(languages) > 1 else str(languages[0].replace('\n', '')).strip()

            # target
            entrance_number_fr = response.css("section.ovw-technical div.item span.blue-link::text")[2].get()
            entrance_number_fr_clean = str(entrance_number_fr).replace('\n', ' ').strip()

        yield {
            'title': title_clean,
            'image': image_clean,
            'date': date_clean,
            'broadcast_place': broadcast_place_clean,
            'genres': genres_clean,
            'certificate': certificate_clean,
            'synopsis': synopsis_clean,
            'directors': directors_clean,
            'scenarists': scenarists_clean,
            'actors': actors_clean,
            'average_notes_press': average_notes_press,
            'average_notes_spectators': average_notes_spectators,
            'nationality': nationality_clean,
            'distributor': distributor_clean,
            'awards': awards_clean,
            'year_production': year_production_clean,
            'movie_type': movie_type_clean,
            'language': languages_clean,
            'entrance_number_fr': entrance_number_fr_clean,
        }




