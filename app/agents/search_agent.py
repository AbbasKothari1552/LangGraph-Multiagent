from app.tools.google_search_tool import results
from app.state.product_subgraph_state import SubGraphState

from app.core.logging_config import get_logger
logger = get_logger(__name__)


def search_agent(state: SubGraphState) -> SubGraphState:
    """
    Executes a web search for the given product search_query
    using the Google Search tool.
    """
    product = state.get("product_info")
    if not product or "search_query" not in product:
        raise ValueError("Product or search_query missing in state")
    
    # Add a fallback LLM invoke for seach_query if not get from orchestrator
    search_query = product["search_query"]

    try:
        urls = results(search_query)

        # Update state
        state["urls"] = urls

        return state

    except Exception as e:
        raise ValueError(f"google search API failiure: {str(e)}")