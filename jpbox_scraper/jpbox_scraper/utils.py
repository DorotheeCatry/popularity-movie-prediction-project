import csv

def get_scraped_film_ids(csv_path):
    scraped_ids = set()
    try:
        with open(csv_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                scraped_ids.add(row['film_id'])
    except FileNotFoundError:
        pass
    return scraped_ids
