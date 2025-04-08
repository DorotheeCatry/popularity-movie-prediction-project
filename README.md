# 🎬 Allociné Scraper — Brief Project

A Python project using Scrapy to extract detailed movie information from Allociné and store it in a PostgreSQL database.

---

## 📌 Project Overview

This scraper was developed as part of a brief project with the objective of automating the collection, cleaning, and storage of structured movie data. The final dataset is ready for analysis or integration into other applications.

---

## 🎯 Project Objectives
This project was developed as part of a brief with the following goals:

- Automatically collect relevant data about movies.
- Clean, structure, and insert this data into a PostgreSQL database.
- Ensure a clean, scalable, and maintainable codebase.

---

## ⚙️ Tech Stack

- Python 3.x  
- Scrapy (web scraping framework)  
- PostgreSQL (relational database)  
- psycopg2 (Python - PostgreSQL connector)  
- python-dotenv (for environment variables)  

---

## 📂 Project Structure

```bash
POPULARITY_MOVIE_PREDICTION_PROJECT/
│── .venv/
│── allocine_scraper/
│   │── allocine_scraper/
│   │   │── spiders/
│   │   │   │── __init__.py
│   │   │   │── allocine_spider.py
│   │   │── __init__.py
│   │   │── items.py
│   │   │── middlewares.py
│   │   │── pipelines.py
│   │   │── settings.py
│── crawls/
│── scrapy.cfg
│── .env
│── .gitignore
│── README.md
│── requirements.txt
```

---

## 🔎 Scraped Data Structure

Each movie record includes:

| Field           | Type     | Description                       |
|-----------------|----------|-----------------------------------|
| title           | TEXT     | Movie title                       |
| original_title  | TEXT     | Original title                    |
| release_date    | TEXT     | Release date                      |
| duration        | TEXT     | Movie duration                    |
| genres          | TEXT[]   | List of genres                    |
| press_rating    | FLOAT    | Press score                       |
| audience_rating | FLOAT    | Audience score                    |
| director        | TEXT     | Director                          |
| writer          | TEXT     | Writer / Screenwriter             |
| audience        | TEXT     | Target audience                   |
| distributor     | TEXT     | Distributor                       |
| movie_type      | TEXT     | Movie type                        |
| nationality     | TEXT[]   | Nationalities                     |
| languages       | TEXT[]   | Spoken languages                  |
| synopsis        | TEXT     | Movie synopsis                    |
| actors          | TEXT[]   | Main actors                       |

---

## 🔐 Environment Variables (.env)

Your `.env` file should look like this:
```bash
DB_HOST=localhost 
DB_USER=your_postgres_username 
DB_PASSWORD=your_postgres_password 
DB_NAME=allocine
```

Make sure to replace `your_postgres_username` and `your_postgres_password` with your actual PostgreSQL credentials.

---
## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/allocine_scraper.git
cd allocine_scraper
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt

```
3. Launch the scraper:
```bash
scrapy crawl allocine_spider
```

---
## 🗄️ Database Behaviour

Every run of the spider will:
- Drop and recreate the films table.
- Insert clean and structured data.
- Automatically handle: PostgreSQL arrays, Floats conversion, Data cleaning, Log errors on insertion failures.

---
## ✅ Strengths of this project
- Scalable and clean architecture
- Automated data cleaning & normalization
- Efficient error handling
- Ready-to-use PostgreSQL dataset
- Easy to update or re-run regularly
- Adaptable to other websites or data structures

---
## 🤝 Author
Made with Python & Scrapy by Dorothée Catry — 2025.