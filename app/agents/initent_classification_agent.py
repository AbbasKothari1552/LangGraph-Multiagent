
from app.state.main_graph_state import State
from app.core.llm import llm


from app.core.logging_config import get_logger
logger = get_logger(__name__)


def intent_classifier_agent(state: State) -> State:
    """
    Classifies whether the request is product-related or general inquiry.
    This is used in LangGraph conditional_edge to decide the next node.
    """

    query = state.get("query", "")
    docs_text = state.get("doc_text", "")

    # Build classification prompt
    prompt = f"""
        You are an AI that classifies user queries and documents into one of two categories:

        1. "product_related" - If the user query or document text is about finding products, product specifications, pricing, availability, or product dealers.
        2. "general_inquiry" - If it is about anything else (people, hotels, organizations, generic information).

        User Query:
        {query}

        Document Text:
        {docs_text}

        Return only one word:
        - product_related
        - general_inquiry
    """

    response = llm.invoke(prompt)
    intent = response.content.lower()

    # Safety check for unexpected output
    if "product_related" in intent:
        classified_intent = "product_related"
    else:
        classified_intent = "general_inquiry"
    
    # Return a dictionary to update the state
    return {"intent": classified_intent}