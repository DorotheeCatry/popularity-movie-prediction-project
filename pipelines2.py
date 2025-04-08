from itemadapter import ItemAdapter
import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime
from utils import parse_date


class AllocineDatabasePipeline:    
    
    def open_spider(self, spider):
        load_dotenv()

        hostname = os.getenv('DB_HOST', 'localhost')
        username = os.getenv('DB_USER', 'dcatry')
        password = os.getenv('DB_PASSWORD', 'Plasma2020@')
        database = os.getenv('DB_NAME', 'allocine')

        self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
        self.cur = self.connection.cursor()
        spider.logger.info("Connection to the database was successful!")

        # Suppression de la table films si elle existe
        self.cur.execute("DROP TABLE IF EXISTS films")

        # Création de la table films avec la nouvelle structure
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS films(
            id SERIAL PRIMARY KEY,
            title TEXT,
            original_title TEXT,
            release_date DATE,
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
            languages TEXT[],
            synopsis TEXT,
            actors TEXT[]
        )
        """)
        self.connection.commit()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Gestion des ratings
        press_rating = adapter.get('press_rating')
        audience_rating = adapter.get('audience_rating')
        if press_rating:
            press_rating = float(press_rating.replace(',', '.')) if press_rating else None
        if audience_rating:
            audience_rating = float(audience_rating.replace(',', '.')) if audience_rating else None
        
        
        # Gestion de la date
        release_date = adapter.get('release_date')
        if release_date:
            release_date = parse_date(adapter.get('release_date'))

        
        # Gestion des champs de type liste
        genres = adapter.get('genres')
        languages = adapter.get('languages')
        actors = adapter.get('actors')
        nationality = adapter.get('nationality')

        # Convert to proper array format
        nationality = adapter.get('nationality')
        if nationality and isinstance(nationality, str):
            # Convert string to list containing the string
            nationality = [nationality.strip().replace('.', '')]
        
        if languages and isinstance(languages, str):
            languages = [languages.strip()]
        
        if genres and isinstance(genres, str):
            genres = [genres.strip()]
            
        if actors and isinstance(actors, str):
            actors = [actors.strip()]


        # Vérification de l'existence des valeurs avant insertion
        try:
            self.cur.execute('''
                INSERT INTO films(
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
                    actors
                )
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                adapter.get('title'),
                adapter.get('original_title'),
                adapter.get('release_date'),
                adapter.get('duration'),
                genres,
                press_rating,
                audience_rating,
                adapter.get('director'),
                adapter.get('writer'),
                adapter.get('audience'),
                adapter.get('distributor'),
                adapter.get('movie_type'),
                nationality,
                languages,
                adapter.get('synopsis'),
                actors
            ))
            
            self.connection.commit()
            return item

        except psycopg2.Error as e:
            spider.logger.error(f"Error inserting item into database: {e}")
            self.connection.rollback()  # Rollback the transaction on error
            return None  # Optionally return None or the item for retry

    def close_spider(self, spider):
        # Close the cursor and connection
        self.cur.close()
        self.connection.close()
