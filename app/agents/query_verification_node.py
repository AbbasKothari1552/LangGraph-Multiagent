from langgraph.types import interrupt

from app.state.main_graph_state import State

from app.core.logging_config import get_logger
logger = get_logger(__name__)


def query_verification(state: State) -> State:
    """
    Human-in-the-loop node for verifying search results before proceeding.
    """
    logger.info("Starting query verification with human-in-the-loop")

    # Get current products info from state
    products_info = state.get("products_info", {})

    # Create the interrupt with the current products data
    verification = interrupt(
        {
            "message": "Please verify and edit the search results before proceeding",
            "product_info": products_info,
            "query": state.get("query", ""),
            "step": "verification"
        }
    )
    
    logger.info("Interrupt created, waiting for user verification")
    
    # The verification variable will contain the user's verified data
    # when the graph resumes
    return {
        **state, 
        "products_info": verification,
        "verification_completed": True
    }
