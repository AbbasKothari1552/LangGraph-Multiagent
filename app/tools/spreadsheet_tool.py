import os
import sys
import asyncio
from typing import List

from langchain_mcp_adapters.client import MultiServerMCPClient

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

SERVICE_ACCOUNT_PATH = os.environ.get("SERVICE_ACCOUNT_PATH") 
DRIVE_FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID") 

# Global variable to store tools once loaded
_tools = None
_client = None

async def _load_tools_async():
    """Async function to load tools from MCP server"""
    global _tools, _client
    if _tools is None:
        _client = MultiServerMCPClient({
            "sheets": {
                "url": "http://127.0.0.1:8000/mcp/",
                "transport": "streamable_http"
            }
        })
        _tools = await _client.get_tools()
    return _tools

def load_tools_sync():
    """Synchronous wrapper to load tools"""
    global _tools
    if _tools is None:
        try:
            # Try to get existing event loop
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # No event loop exists, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if loop.is_running():
            # If loop is already running, we need to use a different approach
            # This typically happens in Jupyter notebooks or similar environments
            import nest_asyncio
            nest_asyncio.apply()
            _tools = loop.run_until_complete(_load_tools_async())
        else:
            _tools = loop.run_until_complete(_load_tools_async())
    
    return _tools

# Initialize tools synchronously
try:
    tools = load_tools_sync()
except Exception as e:
    print(f"Error loading tools: {e}")
    tools = []

async def get_tools_async():
    """Async function to get tools"""
    return await _load_tools_async()

def cleanup():
    """Cleanup function to close MCP client"""
    global _client
    if _client:
        asyncio.run(_client.close())