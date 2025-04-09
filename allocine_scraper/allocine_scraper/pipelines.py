from itemadapter import ItemAdapter
import psycopg2
import os
from dotenv import load_dotenv
from allocine_scraper.utils import parse_date, convert_to_minutes

class AllocineDatabasePipeline:
    
    # Open the spider and establish the database connection
    def open_spider(self, spider):
        load_dotenv()

        # Database connection details from environment variables
        hostname = os.getenv('DB_HOST', 'localhost')
        username = os.getenv('DB_USER', 'dcatry')
        password = os.getenv('DB_PASSWORD', 'Plasma2020@')
        database = os.getenv('DB_NAME', 'allocine')

        # Establish connection to PostgreSQL database
        self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
        self.cur = self.connection.cursor()
        spider.logger.info("Connection to the database was successful!")

        # Drop existing table and create a new one
        self.cur.execute("DROP TABLE IF EXISTS allocine")
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS allocine(
            id SERIAL PRIMARY KEY,
            title TEXT,
            original_title TEXT,
            release_date TEXT,
            duration TEXT,
            genres TEXT[],
            press_rating NUMERIC,
            audience_rating NUMERIC,
            director TEXT,
            writer TEXT,
            audience TEXT,
            distributor TEXT,
            movie_type TEXT,
            nationality TEXT[],
            languages TEXT,
            synopsis TEXT,
            actors TEXT[],
            box_office_fr NUMERIC,
            box_office_us NUMERIC,
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
        writer = adapter.get('writer')

        # Handle audience and distributor
        audience = adapter.get('audience')
        distributor = adapter.get('distributor')

        # Handle movie_type
        movie_type = adapter.get('movie_type')

        # Handle nationality
        nationality = adapter.get('nationality')
        if nationality and isinstance(nationality, str):
            nationality = [nationality.strip().replace('.', '')]

        # Handle languages
        languages = adapter.get('languages')
        if languages and isinstance(languages, str):
            languages = [languages.strip()]
        
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

        # Handle image_url
        image_url = adapter.get('image_url')
        if image_url:
            image_url = image_url.strip() if image_url else None

        # Insert data into the database if all values are parsed correctly
        try:
            self.cur.execute('''
                INSERT INTO allocine(
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
                    image_url
                )
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                image_url
            ))
            self.connection.commit()
            return item

        except psycopg2.Error as e:
            spider.logger.error(f"Error inserting item into database: {e}")
            self.connection.rollback()  # Rollback the transaction on error
            return None  # Optionally return None or the item for retry

    # Close the spider and database connection
    def close_spider(self, spider):
        # Close the cursor and the connection
        self.cur.close()
        self.connection.close()
