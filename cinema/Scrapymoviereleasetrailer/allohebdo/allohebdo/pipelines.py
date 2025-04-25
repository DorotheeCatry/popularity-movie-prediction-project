from scrapy.exceptions import DropItem

class CleanItemPipeline:
    def process_item(self, item, spider):
        # champs texte simples
        for key in ("title", "director", "synopsis"):
            item[key] = item.get(key, "").strip()

        # optionnels
        for key in ("writer", "distributor"):
            item[key] = (item.get(key) or "").strip() or None

        # lists -> strip
        for key in ("genres", "actors", "producers"):
            item[key] = [v.strip() for v in item.get(key, [])]

        # sessions str ➜ int
        item["sessions"] = int("".join(c for c in str(item.get("sessions", 0)) if c.isdigit()) or 0)

        return item


class DedupPipeline:
    """ Évite les doublons titre+date """
    def __init__(self):
        self.seen = set()

    def process_item(self, item, spider):
        key = (item["title"].lower(), item["release_date"])
        if key in self.seen:
            raise DropItem(f"Doublon {key}")
        self.seen.add(key)
        return item








