import os

from langchain_core.tools import Tool
# Provides access to Google search using CSE API.
from langchain_google_community import GoogleSearchAPIWrapper
from langsmith import traceable

from dotenv import load_dotenv
load_dotenv()

from app.core.logging_config import get_logger
logger = get_logger(__name__)


# Add credentials to environment variables
GOOGLE_CSE_ID = os.environ.get("GOOGLE_CSE_ID") 
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")


# Create a tool for searching Google
search = GoogleSearchAPIWrapper()

@traceable(name="Google CSE")
def results(query):
    try:
        results = search.results(query, 10)
        return [r['link'] for r in results]
    
    except Exception as e:
        
        logger.error(f"[Google CSE] {str(e)}")
        logger.debug("Returning empty list")
        return []


tools = [
    Tool(
        name="google_search",
        description="Search Google for recent results.",
        func=results,
    )
]
