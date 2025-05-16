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
            hours, minutes = time_str.split('h')
            total_minutes = int(hours) * 60 + int(minutes.replace('min', '').strip())
            return total_minutes
        except ValueError:
            return None
    return None

def clean_view_count(raw_string):
    if not raw_string:
        return None
    digits_only = re.sub(r"[^\d]", "", raw_string)
    return int(digits_only) if digits_only else None

def parse_numeric(value):
    if value:
        value = value.strip().replace(' ', '').replace(',', '.')
        try:
            return float(value) if '.' in value else int(value)
        except ValueError:
            return None
    return None

def safe_int_extraction(value):
    if value:
        number_str = re.sub(r"[^\d]", "", str(value))
        try:
            return int(number_str) if number_str else None
        except ValueError:
            logger.warning(f"Failed to extract number from {value}.")
            return None
    return None

def parse_brace_string(s):
    if not s:
        return []
    if s.startswith('{') and s.endswith('}'):
        s = s[1:-1]
    return [item.strip().strip('"') for item in s.split(',') if item.strip()]

def clean_pg_array_field(value):
    if isinstance(value, list):
        cleaned_list = [item.strip() for item in value if item and item.strip()]
    elif isinstance(value, str):
        cleaned_list = [
            item.strip() for item in value
            .replace('{', '')
            .replace('}', '')
            .replace('"', '')
            .replace('\n', '')
            .split(',')
            if item.strip()
        ]
    else:
        return '{}'

    return '{' + ','.join(cleaned_list) + '}'