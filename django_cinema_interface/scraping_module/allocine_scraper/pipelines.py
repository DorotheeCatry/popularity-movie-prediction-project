from dotenv import load_dotenv
from allocine_scraper.utils import parse_date, convert_to_minutes, safe_int_extraction, parse_brace_string, clean_pg_array_field
from itemadapter import ItemAdapter
import psycopg2
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "cinema_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
}

class ReleaseDatabasePipeline:
    def open_spider(self, spider):
        try:
            # Establish connection to PostgreSQL database
            self.connection = psycopg2.connect(**DB_CONFIG)
            self.cur = self.connection.cursor()
            spider.logger.info("Connection to the database was successful!")
        except Exception as e:
            spider.logger.error(f"Database connection error: {e}")
            raise

    def process_item(self, item, spider):
        try:
            adapter = ItemAdapter(item)
            
            # Log the item being processed
            spider.logger.info(f"Processing movie: {adapter.get('title')}")
            
            self.cur.execute('''
                INSERT INTO movie_prediction_movie(
                    title, original_title, release_date, duration, genres,
                    press_rating, audience_rating, director, writer,
                    audience, distributor, movie_type, nationality,
                    languages, synopsis, actors, box_office_fr,
                    box_office_us, showings, trailer_date,
                    trailer_views, trailer_number, trailer_url, image_url
                )
                VALUES (%s, %s, %s, %s, %s::text[], %s, %s, %s::text[],
                        %s::text[], %s, %s, %s, %s::text[], %s::text[],
                        %s, %s::text[], %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (title) DO UPDATE SET
                    original_title = EXCLUDED.original_title,
                    release_date = EXCLUDED.release_date,
                    duration = EXCLUDED.duration,
                    genres = EXCLUDED.genres,
                    press_rating = EXCLUDED.press_rating,
                    audience_rating = EXCLUDED.audience_rating,
                    director = EXCLUDED.director,
                    writer = EXCLUDED.writer,
                    audience = EXCLUDED.audience,
                    distributor = EXCLUDED.distributor,
                    movie_type = EXCLUDED.movie_type,
                    nationality = EXCLUDED.nationality,
                    languages = EXCLUDED.languages,
                    synopsis = EXCLUDED.synopsis,
                    actors = EXCLUDED.actors,
                    box_office_fr = EXCLUDED.box_office_fr,
                    box_office_us = EXCLUDED.box_office_us,
                    showings = EXCLUDED.showings,
                    trailer_date = EXCLUDED.trailer_date,
                    trailer_views = EXCLUDED.trailer_views,
                    trailer_number = EXCLUDED.trailer_number,
                    trailer_url = EXCLUDED.trailer_url,
                    image_url = EXCLUDED.image_url
            ''', (
                adapter.get('title'),
                adapter.get('original_title'),
                parse_date(adapter.get('release_date')),
                adapter.get('duration'),
                adapter.get('genres'),
                adapter.get('press_rating'),
                adapter.get('audience_rating'),
                adapter.get('director'),
                adapter.get('writer'),
                adapter.get('audience'),
                adapter.get('distributor'),
                adapter.get('movie_type'),
                adapter.get('nationality'),
                adapter.get('languages'),
                adapter.get('synopsis'),
                adapter.get('actors'),
                adapter.get('box_office_fr'),
                adapter.get('box_office_us'),
                adapter.get('showings'),
                parse_date(adapter.get('trailer_date')),
                adapter.get('trailer_views'),
                adapter.get('trailer_number'),
                adapter.get('trailer_url'),
                adapter.get('image_url')
            ))
            self.connection.commit()
            spider.logger.info(f"Successfully saved movie: {adapter.get('title')}")
            return item
        except Exception as e:
            spider.logger.error(f"Error saving movie: {e}")
            self.connection.rollback()
            raise

    def close_spider(self, spider):
        if hasattr(self, 'cur'):
            self.cur.close()
        if hasattr(self, 'connection'):
            self.connection.close()
        spider.logger.info("Database connection closed")