import dateparser
import re
import logging

logger = logging.getLogger(__name__)

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
            # Split hours and minutes
            hours, minutes = time_str.split('h')
            total_minutes = int(hours) * 60 + int(minutes.replace('min', '').strip())  # Convert to minutes
            return total_minutes
        except ValueError:
            return None  # In case of format error
    return None

def clean_view_count(raw_string):
    """
    Cleans a view count like '58\u202f190 vues' to return an int: 58190.
    """
    if not raw_string:
        return None
    # Remove all non-numeric characters
    digits_only = re.sub(r"[^\d]", "", raw_string)
    return int(digits_only) if digits_only else None


def parse_numeric(self, value):
    if value:
        value = value.strip().replace(' ', '').replace(',', '.')
        try:
            return float(value) if '.' in value else int(value)
        except ValueError:
            return None  # Return None if the value is not a valid number
    return None


def safe_int_extraction(value):
    """ Extract and convert a numeric value from a string, return None if invalid. """
    if value:
        number_str = re.sub(r"[^\d]", "", value)  # Remove all non-numeric characters
        try:
            return int(number_str) if number_str else None
        except ValueError:
            logger.warning(f"Failed to extract number from {value}.")
            return None
    return None