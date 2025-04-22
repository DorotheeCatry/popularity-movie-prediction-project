from scrapy.exceptions import DropItem

class CleanTrailerPipeline:
    def process_item(self, item, spider):
        try:
            item["vues"] = int(item["vues"])
        except (TypeError, ValueError):
            raise DropItem(f"Invalid vues: {item.get('vues')}")

        ds = item.get("date_sortie")
        if not isinstance(ds, str):
            raise DropItem(f"Invalid date_sortie: {ds}")
        return item

