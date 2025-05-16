from dotenv import load_dotenv
from .utils import parse_date, convert_to_minutes, safe_int_extraction, parse_brace_string, clean_pg_array_field
from itemadapter import ItemAdapter
import psycopg2
import os
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

load_dotenv()

class ReleaseDatabasePipeline:
    def open_spider(self, spider):
        load_dotenv()
        
        DB_CONFIG = {
            "dbname": os.getenv("DB_NAME", "cinema_db"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD", "postgres"),
            "host": os.getenv("DB_HOST", "localhost"),
            "port": os.getenv("DB_PORT", "5432"),
        }

        self.connection = psycopg2.connect(**DB_CONFIG)
        self.cur = self.connection.cursor()
        spider.logger.info("Connection to the database was successful!")

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Process all fields
        title = adapter.get('title')
        original_title = adapter.get('original_title')
        release_date = parse_date(adapter.get('release_date'))
        duration = convert_to_minutes(adapter.get('duration'))
        genres = adapter.get('genres')
        press_rating = adapter.get('press_rating')
        audience_rating = adapter.get('audience_rating')
        director = adapter.get('director')
        writer = adapter.get('writer')
        audience = adapter.get('audience')
        distributor = adapter.get('distributor')
        movie_type = adapter.get('movie_type')
        nationality = clean_pg_array_field(adapter.get('nationality'))
        languages = clean_pg_array_field(adapter.get('languages'))
        synopsis = adapter.get('synopsis')
        actors = adapter.get('actors')
        box_office_fr = safe_int_extraction(adapter.get('box_office_fr'))
        box_office_us = safe_int_extraction(adapter.get('box_office_us'))
        showings = safe_int_extraction(adapter.get('showings'))
        trailer_date = parse_date(adapter.get('trailer_date'))
        trailer_views = safe_int_extraction(adapter.get('trailer_views'))
        trailer_number = safe_int_extraction(adapter.get('trailer_number'))
        trailer_url = adapter.get('trailer_url')
        image_url = adapter.get('image_url')

        try:
            self.cur.execute('''
                INSERT INTO movie_prediction_movie(
                    title, original_title, release_date, duration, genres,
                    press_rating, audience_rating, director, writer,
                    audience, distributor, movie_type, nationality,
                    languages, synopsis, actors, box_office_fr,
                    box_office_us, showings, trailer_date, trailer_views,
                    trailer_number, trailer_url, image_url
                )
                VALUES(%s, %s, %s, %s, %s::text[], %s, %s, %s::text[], %s::text[],
                       %s, %s, %s, %s::text[], %s::text[], %s, %s::text[],
                       %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                title, original_title, release_date, duration, genres,
                press_rating, audience_rating, director, writer,
                audience, distributor, movie_type, nationality,
                languages, synopsis, actors, box_office_fr,
                box_office_us, showings, trailer_date, trailer_views,
                trailer_number, trailer_url, image_url
            ))
            self.connection.commit()
            return item
        except Exception as e:
            spider.logger.error(f"Error inserting item into database: {e}")
            self.connection.rollback()
            return None

    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()