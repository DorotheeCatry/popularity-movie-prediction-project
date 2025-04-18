import pandas as pd
from datetime import timedelta
from config import DB_CONFIG
import psycopg2
import snscrape.modules.twitter as sntwitter
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sqlalchemy import create_engine
import time
import re
import unicodedata
import ssl
import requests
import os
import certifi
from dotenv import load_dotenv

load_dotenv()


def get_movies_from_db():
    """Retrieve all movie titles and release dates from PostgreSQL."""
    query = """
        SELECT id, title, release_date
        FROM allocine_cleaned
        WHERE release_date IS NOT NULL
        ORDER BY release_date DESC;
    """
    try:
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_name = os.getenv("DB_NAME")

        # On laisse 'localhost' ici, car 'connect_args' va forcer l'usage de 127.0.0.1
        db_url = f"postgresql+psycopg2://{db_user}:{db_password}@localhost:5432/{db_name}"

        engine = create_engine(db_url, connect_args={"host": "127.0.0.1"})
        with engine.connect() as connection:
            df = pd.read_sql(query, con=connection)
        return df
    except Exception as e:
        print(f"Database connection error: {e}")
        return pd.DataFrame()

def clean_title(title: str) -> str:
    # Normalisation unicode (é → e)
    title = unicodedata.normalize("NFD", title)
    title = title.encode("ascii", "ignore").decode("utf-8")
    # Suppression des caractères non alphanumériques (sauf espace)
    title = re.sub(r"[^\w\s]", "", title)
    # Suppression des espaces en trop
    return title.strip()

def get_tweets(title, release_date, lang="fr", max_results=100):
    start_date = release_date - timedelta(days=7)
    end_date = release_date
    
    title_processed = clean_title(title).replace(' ', '')
    title_query = f'#{title_processed}'
    
    #context_words = '"film" OR "cinéma" OR "vu" OR "sortie" OR "bande-annonce"'
    #start_date = release_date - timedelta(days=7)
    #end_date = release_date
    #date_filter = f"since:{start_date} until:{end_date}"
    #lang_filter = f"lang:{lang}"
    
    query = f'{title_query} lang:{lang} since:{start_date} until:{end_date}'

    
    tweets = []
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
        if i >= max_results:
            break
        tweets.append({
            "date": tweet.date,
            "content": tweet.content,
            "likeCount": tweet.likeCount,
            "retweetCount": tweet.retweetCount,
        })
        # Ajouter un délai de 1 seconde entre chaque requête
        time.sleep(5)
    return pd.DataFrame(tweets)

def analyze_sentiments(tweets_df):
    analyzer = SentimentIntensityAnalyzer()
    tweets_df["sentiment"] = tweets_df["content"].apply(lambda x: analyzer.polarity_scores(x)["compound"])
    return tweets_df

def aggregate_weekly_metrics(tweets_df):
    if tweets_df.empty:
        return {
            "nb_tweets": 0,
            "total_likes": 0,
            "total_retweets": 0,
            "avg_sentiment": None,
            "max_sentiment": None,
            "min_sentiment": None
        }
    return {
        "nb_tweets": len(tweets_df),
        "total_likes": tweets_df["likeCount"].sum(),
        "total_retweets": tweets_df["retweetCount"].sum(),
        "avg_sentiment": tweets_df["sentiment"].mean(),
        "max_sentiment": tweets_df["sentiment"].max(),
        "min_sentiment": tweets_df["sentiment"].min(),
    }

def save_metrics_to_db(film_id, metrics):
    query = """
        INSERT INTO twitter_metrics (
            film_id, nb_tweets, total_likes, total_retweets,
            avg_sentiment, max_sentiment, min_sentiment
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (film_id) DO UPDATE SET
            nb_tweets = EXCLUDED.nb_tweets,
            total_likes = EXCLUDED.total_likes,
            total_retweets = EXCLUDED.total_retweets,
            avg_sentiment = EXCLUDED.avg_sentiment,
            max_sentiment = EXCLUDED.max_sentiment,
            min_sentiment = EXCLUDED.min_sentiment;
    """
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (
                    film_id,
                    metrics["nb_tweets"],
                    metrics["total_likes"],
                    metrics["total_retweets"],
                    metrics["avg_sentiment"],
                    metrics["max_sentiment"],
                    metrics["min_sentiment"]
                ))
                conn.commit()
                print(f"Metrics saved for movie {film_id}.")
    except Exception as e:
        print(f"Error inserting metrics into the database: {e}")

def main():
    print("Starting weekly Twitter sentiment aggregation...")
    movies_df = get_movies_from_db()

    if movies_df.empty:
        print("No movies found or database error.")
        return

    for _, row in movies_df.iterrows():
        film_id = row["id"]
        title = row["title"]
        release_date = row["release_date"]

        print(f"\nProcessing {title} ({release_date})")
        tweets_df = get_tweets(title, release_date)
        tweets_df = analyze_sentiments(tweets_df)
        metrics = aggregate_weekly_metrics(tweets_df)
        save_metrics_to_db(film_id, metrics)

if __name__ == "__main__":
    main()





