<!-- Banner Image -->
![Cinema Banner](https://media.istockphoto.com/id/1494642262/fr/photo/les-gens-dans-lauditorium-de-cin%C3%A9ma-avec-%C3%A9cran-blanc-vide.webp?a=1&b=1&s=612x612&w=0&k=20&c=O_xUXPdWdVOXkmMBq7dC9yWoc5zkgnHwe4UJ9mSa1xY=)

# <span style="color:#2E86C1;">JPBox Scraper</span>

Welcome to the <span style="color:#E74C3C;">JPBox Scraper</span> project – an advanced web scraping solution dedicated to gathering film data from [jpbox-office.com](https://www.jpbox-office.com). This repository contains the complete Scrapy and Selenium based spider along with tools to manage CSV backups and merge your scraped results. If the code crashes during execution, simply rename your CSV file as directed and merge the backup as documented below.

---

## 🎬 Project Overview

- **Spider**: The core class `FilmsSeleniumSpider` (located in `films_spider.py`) handles the dynamic scraping of film details using Selenium.
- **Data Files**:
  - **`films.csv`**: Contains the newest scraped film data.
  - **`films_backup.csv`**: Acts as a backup to store previously scraped film IDs to avoid duplicates.
- **Merge Notebook**: A Jupyter Notebook helps to merge the backup CSV with the new data, ensuring that no film entry is duplicated and that all data remains consistent.

---

## 🚀 Dependencies & Setup

This project requires:

- **Python 3.8+**  
- **Scrapy**  
- **Selenium**  
- **ChromeDriver** (or an equivalent browser driver for Selenium)

### Installation

Create a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate  # For Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🔍 Running the Scraper

1. **Navigate** to the scraper directory:
   ```bash
   cd jpbox_scraper
   ```

2. **Run the spider**:
   ```bash
   scrapy crawl films
   ```
   This command launches Selenium in headless mode and starts the scraping process. The spider will:
   - Dynamically scroll the page until at least 30 rows are gathered or no additional content loads.
   - Check for duplicate film entries by comparing against `films_backup.csv`.
   - Write new results into `films.csv`.

---

## 💾 Handling Backups & Merging

### If the Scraper Crashes or Stops Early

1. **Rename the current CSV file:**

   If your scraping run gets interrupted, rename `films.csv` to create a backup:
   ```bash
   mv films.csv films_backup.csv
   ```

2. **Re-run the Scraper:**
   ```bash
   scrapy crawl films
   ```

3. **Merge the Data:**
   Use the provided merge notebook to combine `films_backup.csv` with the new `films.csv`. The notebook:
   - Reads both CSV files.
   - Removes duplicates based on `film_id`.
   - Consolidates the data into a unified, complete dataset.

### First-Time Execution

- On the initial run, simply execute the spider to generate `films.csv`. Later, if merging is needed, rename it as described above.

---

## 🛠 Additional Notes & Troubleshooting

- **Custom Settings**:  
  The spider’s `custom_settings` ensure CSV fields remain in a fixed order and activate debugging options for duplicate filtering.

- **Dynamic Scrolling**:  
  Modify the `time.sleep()` durations in the `process_page` method if you experience network delays.

- **Driver Configuration**:  
  Ensure your `chromedriver` matches your browser version. For Linux systems, you might need to adjust the binary location (e.g., `/usr/bin/chromium-browser`).

- **Logging**:  
  All log messages from Scrapy will be output to the console – monitor these for real-time error reporting.

---

## 📂 Code Structure

- **`films_spider.py`**: Contains the complete implementation of the `FilmsSeleniumSpider` class.
- **`utils.py`**: Includes helper functions like `get_scraped_film_ids` to load existing film IDs from `films_backup.csv`.
- **Merge Notebook**: A Jupyter Notebook designed to merge CSV files, ensuring data integrity and no duplicate entries.

---

<!-- Footer with another image -->
<div style="text-align: center; margin-top: 20px;">
  <img src="https://media.istockphoto.com/id/1289323170/fr/photo/concept-de-contenu-visuel-service-de-r%C3%A9seautage-social-vid%C3%A9o-en-streaming-r%C3%A9seau-de.webp?a=1&b=1&s=612x612&w=0&k=20&c=BSb9hsRNso67ip3VW9KxEY3xBLVYHl5lo9O5kYQ7D7A=" alt="Film Project" />
</div>

<span style="color:#27AE60; font-size:1.2em;">
Happy Scraping and Cinephile Coding!
</span>
