from typing import TypedDict, Dict, List, Annotated
import operator

class SubGraphState(TypedDict):
    product_info: dict
    urls: list
    product_data: Dict[str, list]
    scraped_data: Annotated[List[dict], operator.add]
