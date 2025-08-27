from typing import TypedDict, Dict, List, Annotated
import operator


class State(TypedDict):
    file_dir: str
    extracted_text_dir: str
    extracted_text_path: str
    file_path: str
    file_name: str
    extraction_method: str
    extraction_status: str
    doc_text: str
    query: str
    route: str
    intent: str
    available_mcp_servers: list
    products_info: dict
    product_data: Annotated[dict, operator.or_] # dict merge with |