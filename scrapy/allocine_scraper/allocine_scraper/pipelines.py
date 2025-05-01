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
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}


class AllocineDatabasePipeline:
    
    # Open the spider and establish the database connection
    def open_spider(self, spider):
        load_dotenv()

        # Establish connection to PostgreSQL database
        self.connection = psycopg2.connect(**DB_CONFIG)
        self.cur = self.connection.cursor()
        spider.logger.info("Connection to the database was successful!")

        # Drop existing table and create a new one
        self.cur.execute("DROP TABLE IF EXISTS allocine_movies")
        
        # Create the table with the specified schema
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS allocine_movies(
            id SERIAL PRIMARY KEY,
            title TEXT,
            original_title TEXT,
            release_date DATE,
            duration INTEGER,
            genres TEXT[],
            press_rating NUMERIC,
            audience_rating NUMERIC,
            director TEXT[],
            writer TEXT[],
            audience TEXT,
            distributor TEXT,
            movie_type TEXT,
            nationality TEXT[],
            languages TEXT[],
            synopsis TEXT,
            actors TEXT[],
            box_office_fr NUMERIC,
            total_box_office_fr NUMERIC,
            box_office_us NUMERIC,
            total_box_office_us NUMERIC,
            showings INTEGER,
            trailer_date DATE,
            trailer_views INTEGER,
            trailer_number INTEGER,
            image_url TEXT
        )
        """)
        self.connection.commit()

    # Process each scraped item and insert into the database
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Handle title and original_title
        title = adapter.get('title')
        original_title = adapter.get('original_title')

        # Handle release_date
        release_date = adapter.get('release_date')
        if release_date:
            release_date = parse_date(release_date)

        # Handle duration
        duration = adapter.get('duration')
        if duration:
            duration = convert_to_minutes(duration)

        # Handle genres
        genres = adapter.get('genres')
        if genres and isinstance(genres, str):
            genres = [genres.strip()]

        # Handle press_rating and audience_rating
        press_rating = adapter.get('press_rating')
        if press_rating:
            press_rating = float(press_rating.replace(',', '.')) if press_rating else None
        audience_rating = adapter.get('audience_rating')
        if audience_rating:
            audience_rating = float(audience_rating.replace(',', '.')) if audience_rating else None


        # Handle director and writer
        director = adapter.get('director')
        if director and isinstance(director, str):
            director = [parse_brace_string(item) for item in director]
            director = [item.strip() for sublist in director for item in sublist]
            
            
        writer = adapter.get('writer')
        if writer and isinstance(writer, str):
            writer = [parse_brace_string(item) for item in writer]
            writer = [item.strip() for sublist in writer for item in sublist]

        # Handle audience and distributor
        audience = adapter.get('audience')
        
        distributor = adapter.get('distributor')
        distributor = distributor.strip() if distributor else None

        # Handle movie_type
        movie_type = adapter.get('movie_type')

        # Handle nationality
        nationality = adapter.get('nationality')
        if nationality :
            nationality = clean_pg_array_field(nationality)

        # Handle languages
        languages = adapter.get('languages')
        if languages :
            languages = clean_pg_array_field(languages)
            
        # Handle synopsis
        synopsis = adapter.get('synopsis')

        # Handle actors
        actors = adapter.get('actors')
        if actors and isinstance(actors, str):
            actors = [actors.strip()]

        # Handle box_office_fr and box_office_us
        
        box_office_fr = adapter.get('box_office_fr')
        if box_office_fr:
            box_office_fr = int(box_office_fr.replace(' ', '')) if box_office_fr else None
        
        box_office_us = adapter.get('box_office_us')
        if box_office_us:
            box_office_us = int(box_office_us.replace(' ', '')) if box_office_us else None

        total_box_office_fr = adapter.get('total_box_office_fr')
        if total_box_office_fr and isinstance(total_box_office_fr, str):
            total_box_office_fr = safe_int_extraction(total_box_office_fr)
            
        total_box_office_us = adapter.get('total_box_office_us')
        if total_box_office_us and isinstance(total_box_office_us, str):
            total_box_office_us = safe_int_extraction(total_box_office_us)

        
        showings = adapter.get('showings')
        trailer_views = adapter.get('trailer_views')
        trailer_number = adapter.get('trailer_number')

        # Safely extract and convert the values
        showings = safe_int_extraction(showings)
        trailer_views = safe_int_extraction(trailer_views)
        trailer_number = safe_int_extraction(trailer_number)
        
        trailer_date = adapter.get('trailer_date')
        if trailer_date:
            trailer_date = parse_date(trailer_date) if trailer_date else None

        # Handle image_url
        image_url = adapter.get('image_url')
        if image_url:
            image_url = image_url.strip()

        # Insert data into the database if all values are parsed correctly
        try:
            self.cur.execute('''
            INSERT INTO allocine_movies(
            title,
            original_title,
            release_date,
            duration,
            genres,
            press_rating,
            audience_rating,
            director,
            writer,
            audience,
            distributor,
            movie_type,
            nationality,
            languages,
            synopsis,
            actors,
            box_office_fr,
            total_box_office_fr,
            box_office_us,
            total_box_office_us,
            showings,
            trailer_date,
            trailer_views,
            trailer_number,
            image_url
                    )
                VALUES(%s, %s, %s, %s, %s::text[], %s, %s, %s::text[], %s::text[], %s, %s, %s, %s, %s::text[], %s, %s::text[], %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
            title,
            original_title,
            release_date,
            duration,
            genres,
            press_rating,
            audience_rating,
            director,
            writer,
            audience,
            distributor,
            movie_type,
            nationality,
            languages,
            synopsis,
            actors,
            box_office_fr,
            total_box_office_fr,
            box_office_us,
            total_box_office_us,
            showings,
            trailer_date,
            trailer_views,
            trailer_number,
            image_url
            ))
            self.connection.commit()
            spider.logger.info(f"Successfully inserted {title} into database")
            return item

        except Exception as e:
            spider.logger.error(f"Error processing item: {e}")
            self.connection.rollback()
            return item

    def close_spider(self, spider):
        """Close database connection when spider closes."""
        if self.connection:
            self.cur.close()
            self.connection.close()
            spider.logger.info("Database connection closed")

class ReleaseDatabasePipeline:
    
    # Open the spider and establish the database connection
    def open_spider(self, spider):
        load_dotenv()

        # Establish connection to PostgreSQL database
        self.connection = psycopg2.connect(**DB_CONFIG)
        self.cur = self.connection.cursor()
        spider.logger.info("Connection to the database was successful!")

        # Drop existing table and create a new one
        self.cur.execute("DROP TABLE IF EXISTS newrelease")
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS newrelease(
            id SERIAL PRIMARY KEY,
            title TEXT,
            original_title TEXT,
            release_date DATE,
            duration TEXT,
            genres TEXT[],
            press_rating NUMERIC,
            audience_rating NUMERIC,
            director TEXT[],
            writer TEXT[],
            audience TEXT,
            distributor TEXT,
            movie_type TEXT,
            nationality TEXT[],
            languages TEXT[],
            synopsis TEXT,
            actors TEXT[],
            box_office_fr NUMERIC,
            box_office_us NUMERIC,
            showings NUMERIC,
            trailer_date DATE,
            trailer_views NUMERIC,
            trailer_number NUMERIC,
            trailer_url TEXT,
            image_url TEXT
        )
        """)
        self.connection.commit()

    # Process each scraped item and insert into the database
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Handle title and original_title
        title = adapter.get('title')
        original_title = adapter.get('original_title')

        # Handle release_date
        release_date = adapter.get('release_date')
        if release_date:
            release_date = parse_date(release_date)

        # Handle duration
        duration = adapter.get('duration')
        if duration:
            duration = convert_to_minutes(duration)

        # Handle genres
        genres = adapter.get('genres')
        if genres and isinstance(genres, str):
            genres = [genres.strip()]

        # Handle press_rating and audience_rating
        press_rating = adapter.get('press_rating')
        if press_rating:
            press_rating = float(press_rating.replace(',', '.')) if press_rating else None
        audience_rating = adapter.get('audience_rating')
        if audience_rating:
            audience_rating = float(audience_rating.replace(',', '.')) if audience_rating else None


        # Handle director and writer
        director = adapter.get('director')
        if director and isinstance(director, str):
            director = [parse_brace_string(item) for item in director]
            director = [item.strip() for sublist in director for item in sublist]
            
            
        writer = adapter.get('writer')
        if writer and isinstance(writer, str):
            writer = [parse_brace_string(item) for item in writer]
            writer = [item.strip() for sublist in writer for item in sublist]

        # Handle audience and distributor
        audience = adapter.get('audience')
        
        distributor = adapter.get('distributor')
        distributor = distributor.strip() if distributor else None

        # Handle movie_type
        movie_type = adapter.get('movie_type')

        # Handle nationality
        nationality = adapter.get('nationality')
        if nationality :
            nationality = clean_pg_array_field(nationality)

        # Handle languages
        languages = adapter.get('languages')
        if languages :
            languages = clean_pg_array_field(languages)
            
        # Handle synopsis
        synopsis = adapter.get('synopsis')

        # Handle actors
        actors = adapter.get('actors')
        if actors and isinstance(actors, str):
            actors = [actors.strip()]

        # Handle box_office_fr and box_office_us
        box_office_fr = adapter.get('box_office_fr')
        if box_office_fr:
            box_office_fr = int(box_office_fr.replace(' ', '')) if box_office_fr else None
        box_office_us = adapter.get('box_office_us')
        if box_office_us:
            box_office_us = int(box_office_us.replace(' ', '')) if box_office_us else None
        
        showings = adapter.get('showings')
        trailer_views = adapter.get('trailer_views')
        trailer_number = adapter.get('trailer_number')

        # Safely extract and convert the values
        showings = safe_int_extraction(showings)
        trailer_views = safe_int_extraction(trailer_views)
        trailer_number = safe_int_extraction(trailer_number)
        
        trailer_date = adapter.get('trailer_date')
        if trailer_date:
            trailer_date = parse_date(trailer_date) if trailer_date else None

        trailer_url = adapter.get('trailer_url')
        if trailer_url:
            trailer_url = trailer_url.strip() if trailer_url else None

        # Handle image_url
        image_url = adapter.get('image_url')
        if image_url:
            image_url = image_url.strip()

        # Insert data into the database if all values are parsed correctly
        try:
            self.cur.execute('''
                INSERT INTO newrelease(
                    title,
                    original_title,
                    release_date,
                    duration,
                    genres,
                    press_rating,
                    audience_rating,
                    director,
                    writer,
                    audience,
                    distributor,
                    movie_type,
                    nationality,
                    languages,
                    synopsis,
                    actors,
                    box_office_fr,
                    box_office_us,
                    showings,
                    trailer_date,
                    trailer_views,
                    trailer_number,
                    trailer_url,
                    image_url
                    )
                VALUES(%s, %s, %s, %s, %s::text[], %s, %s, %s::text[], %s::text[], %s, %s, %s, %s, %s::text[], %s, %s::text[], %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                title,
                original_title,
                release_date,
                duration,
                genres,
                press_rating,
                audience_rating,
                director,
                writer,
                audience,
                distributor,
                movie_type,
                nationality,
                languages,
                synopsis,
                actors,
                box_office_fr,
                box_office_us,
                showings,
                trailer_date,
                trailer_views,
                trailer_number,
                trailer_url,
                image_url
            ))
            self.connection.commit()
            return item

        except psycopg2.Error as e:
            spider.logger.error(f"Error inserting item into database: {e}")
            self.connection.rollback()  # Rollback the transaction on error
            return None  # Optionally return None or the item for retry
