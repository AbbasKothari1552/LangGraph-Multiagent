from langgraph.constants import Send
from typing import List

# import states
from app.state.main_graph_state import State
from app.state.product_subgraph_state import SubGraphState
from app.state.scrape_subgraph_state import ScrapeSubGraphState


def route_from_start(state: State) -> str:
    if not state.get("file_path"):
        return "IntentClassifier"  # No file, go directly
    return "ParserAgent"  # File present, parse it


# Conditional 2: Decide orchestrator path
def route_from_intent(state: State) -> str:
    """Return 'ProductOrchestrator' or 'GeneralOrchestrator'."""
    intent = state.get("intent", "")
    if intent == "product_related":
        return "ProductOrchestrator"
    return "GeneralOrchestrator"

def fanout_products_node(state: State) -> List[Send]:
    """
    Takes orchestrator_output["products"] and sends each product
    into the subgraph in parallel.
    """
    products = state.get("products_info").get("products", [])
    sends: List[Send] = []

    print(f"[DEBUG] Count of Products: {len(products)}")

    for product in products:
        # Skip invalid or empty products
        if not product or not isinstance(product, dict) or "name" not in product:
            print("Skipping invalid product in fanout:", product)
            continue
        sub_state: SubGraphState = {
            "product_info": product,
            "urls": [],
            "product_data": {},
            "scraped_data": []
        }
        sends.append(Send("ProductSubgraph", sub_state))  # "ProductSubgraph" must match your subgraph node name

    
    print("DEBUG: fanout sending branches =", len(sends))

    return sends

def fanout_scrape_node(state: SubGraphState) -> List[Send]:

    urls = state.get("urls")
    product_info = state.get("product_info")

    sends: List[Send] = []

    print(f"[DEBUG] Count of URLs: {len(urls)}")

    for url in urls:

        sub_state: ScrapeSubGraphState = {
            "url": url,
            "information": product_info,
            "scraped_data": []
        }
        sends.append(Send("ScrapeSubgraph", sub_state))
    
    print("DEBUG: fanout sending branches =", len(sends))

    return sends