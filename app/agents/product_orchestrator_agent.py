import json
from datetime import datetime

from app.state.main_graph_state import State
from app.core.llm import llm

from app.core.logging_config import get_logger
logger = get_logger(__name__)


def product_orchestrator(state:State) -> State:
    query = state.get("query", "")
    docs_text = state.get("doc_text", "")
    available_mcp_servers = state.get("available_mcp_servers", [])

    system_prompt = """
        You are a Product Orchestrator.

        You must STRICTLY return only valid JSON and nothing else.

        Your responsibilities:
        1. Understand the user's query and any provided document text.
        2. Extract every unique product mentioned.
        3. Determine the type of information the user is looking for:
            - "product_details" → product specifications, features, technical details.
            - "dealer_details" → dealer/shop name, owner, contact info, location.
            - "both" → if both are required.
        4. For each product:
            - Write a short description of the product (1–2 sentences).
            - Based on the information type, generate a dictionary of necessary fields for scraping, with clear descriptions.
            - Always include a "url" field with description: "The source URL where this information was found."
            - Decide which sources to use for this product: "mcp", "web", or both.
            - "Generate a **dealer-optimized search_query** string. 
                - Always include keywords like 'authorized dealer', 'distributor', 'wholesale', 'supplier', 'reseller'. 
                - If location is in user query, include it (e.g., 'Dell laptop authorized dealers in Mumbai').
                - Use Google operators when useful:
                -   - site:.in or site:.com for region/company domains
                -   - intitle:dealer OR intitle:distributor
                - Avoid generic shopping sites like Amazon/Flipkart."

        Output format:
        {
            "products": [
                {
                    "name": "string",
                    "description": "string",
                    "information_type": "product_details" | "dealer_details" | "both",
                    "fields": {
                        "field_name": "field description"
                    },
                    "sources": ["mcp", "web"],
                    "search_query": "string"
                }
            ]
        }

        Rules:
        - The "search_query" must be optimized for direct use in a search engine.
        - Only output valid JSON.

    """

    user_prompt = f"""
        User query:
        {query}

        Document text:
        {docs_text}

        Available MCP servers:
        {available_mcp_servers}
    """

    response = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ])

    try:
        products_info = json.loads(response.content)
    except json.JSONDecodeError:
        logger.error(f"LLM did not return valid JSON.")
        logger.debug(f"invoking LLM for fixing the json format")
        
        data = llm.invoke("Fix this JSON: " + response.content)

        try:
            products_info = json.loads(data)
        except json.JSONDecodeError:
            raise ValueError("LLM did not return valid JSON.")

    state["products_info"] = products_info
    state["file_name"] = str(datetime.now())
    return state