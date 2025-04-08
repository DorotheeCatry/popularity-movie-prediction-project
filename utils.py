def parse_date(date_str):
    if not date_str:
        return None
    try:
        # Transformation manuelle du mois en nombre
        months_fr = {
            'janvier': '01',
            'février': '02',
            'mars': '03',
            'avril': '04',
            'mai': '05',
            'juin': '06',
            'juillet': '07',
            'août': '08',
            'septembre': '09',
            'octobre': '10',
            'novembre': '11',
            'décembre': '12'
        }

        parts = date_str.lower().split()
        if len(parts) == 3:
            day = parts[0].zfill(2)  # zero-padding
            month = months_fr.get(parts[1])
            year = parts[2]
            if month:
                return f"{year}-{month}-{day}"  # format YYYY-MM-DD
        return None
    except Exception:
        return None