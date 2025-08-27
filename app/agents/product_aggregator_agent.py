from app.state.product_subgraph_state import SubGraphState

from app.core.logging_config import get_logger
logger = get_logger(__name__)

def product_aggregator(state: SubGraphState) -> SubGraphState:

    product_info = state.get("product_info", {})
    product_name = product_info["name"]

    scraped_data = state.get("scraped_data", [])

    if scraped_data:
        state["product_data"].setdefault(product_name, [])
        state["product_data"][product_name].extend(scraped_data)
        print(f"Added {len(scraped_data)} records to state for schema '{product_name}'.")
    else:
        print(f"No valid data collected for schema '{product_name}'.")

    return state

