from typing import TypedDict, Dict, List

class ScrapeSubGraphState(TypedDict):
    url: str
    information: dict
    scraped_data: List[dict]