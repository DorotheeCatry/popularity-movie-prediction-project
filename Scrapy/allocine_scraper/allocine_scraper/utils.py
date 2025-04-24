import dateparser

def parse_date(date_str):
    if not date_str:
        return None
    date = dateparser.parse(date_str, languages=['fr'])
    if date:
        return date.strftime('%Y-%m-%d')
    return None

def convert_to_minutes(time_str):
    if time_str:
        try:
            # Séparation de l'heure et des minutes
            hours, minutes = time_str.split('h')
            total_minutes = int(hours) * 60 + int(minutes.replace('min', '').strip())  # Conversion en minutes
            return total_minutes
        except ValueError:
            return None  # En cas d'erreur dans le format
    return None