import scrapy
from scrapy import Field

class FilmscraperParsingItem(scrapy.Item):
    titre = Field()
    titre_original = Field()
    infos = Field()
    infos_technique = Field()
    realisateur = Field()
    only_realisateur = Field()
    nationalite = Field()
    description = Field()
    ratings = Field()
    duration = Field()
    public = Field()
    acteurs = Field()
    type = Field()
