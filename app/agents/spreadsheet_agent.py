import os
import sys
import asyncio

from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage

from app.state.main_graph_state import State
from app.tools.spreadsheet_tool import tools
from core.llm import llm


def spreadsheet_agent(state: State) -> State:
    """
    Spreadsheet agent that creates a Google Sheet and inserts product data.
    """
    filename = state.get("file_name", "")
    product_data = state.get("product_data", {})

    # Check if we have the required data
    if not filename:
        print("Warning: No filename provided in state")
        state["spreadsheet_error"] = "No filename provided"
        return state
    
    if not product_data:
        print("Warning: No product data provided in state")
        state["spreadsheet_error"] = "No product data provided"
        return state

    try:
        agent = create_react_agent(
            llm, 
            tools
        )

        # System prompt for guiding the agent
        instructions = f"""
        You are a spreadsheet automation agent with access to spreadsheet tools.

        Rules:
        - If any tool call fails (e.g., authentication required, network error), you MUST resolve the error (by calling the correct tool) and then RETRY the same failed step before proceeding.
        - Never skip or reorder steps after an error. Always continue from the failed step.
        - Never create a worksheet before a spreadsheet exists.
        - Never insert rows before headers exist.

        Your responsibilities:
        1. Create a spreadsheet with the name provided in "document_name".
        2. For each product in "products":
        - Create a worksheet named exactly as the product name.
        - Add the first row as headers (keys of the data dictionary).
        - Insert all rows of product data into that worksheet below the headers.
        3. After inserting all data, confirm completion.

        Finally, always provide a structured summary with:
        - Spreadsheet Name
        - Worksheets Created with row counts
        - A preview (first 2 rows) of each worksheet's data
        - Mark "0 rows" if a worksheet had no data

        """

        user_prompt = f"""
            Document Name: {filename}

            Products:
            {product_data}

        """

        print(f"🔹 Invoking spreadsheet agent with filename: {filename}")
        # print(f"🔹 Product data keys: {list(product_data.keys()) if isinstance(product_data, dict) else 'Not a dict'}")

        response = asyncio.run(agent.ainvoke({
            "messages": [
                SystemMessage(content=instructions),
                HumanMessage(content=user_prompt)
            ]
        })) 

        # Update state with the response
        if response and "messages" in response:
            final_message = response["messages"][-1].content if response["messages"] else "No response content"
            state["spreadsheet_response"] = final_message
            state["spreadsheet_status"] = "completed"
            print(f"✅ Spreadsheet agent completed successfully")
        else:
            state["spreadsheet_error"] = "No response from agent"
            state["spreadsheet_status"] = "failed"
            print(f"❌ Spreadsheet agent failed: No response")

    except Exception as e:
        error_msg = f"Error in spreadsheet agent: {str(e)}"
        print(f"❌ {error_msg}")
        state["spreadsheet_error"] = error_msg
        state["spreadsheet_status"] = "failed"

    return state





