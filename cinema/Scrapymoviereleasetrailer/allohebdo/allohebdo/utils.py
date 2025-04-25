from datetime import datetime

_FR_MONTHS = {
    "janvier": 1, "février": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6,
    "juillet": 7, "août": 8, "septembre": 9, "octobre": 10,
    "novembre": 11, "décembre": 12,
}

def parse_french_date(text: str) -> datetime | None:
    """
    '30 avril 2025' ➜ datetime(2025, 4, 30)  |  renvoie None si parsing impossible
    """
    try:
        day, month_fr, year = text.lower().split()
        return datetime(int(year), _FR_MONTHS[month_fr], int(day))
    except Exception:
        return None




