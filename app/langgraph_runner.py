from langgraph.types import Command

from app.core.config import UPLOAD_DIR, EXTRACTED_CONTENT_DIR
from app.workflow.main_workflow import graph
# from app.workflow.interrupt import graph

# thread = {"configurable": {"thread_id": "1"}}

# Global storage for thread states (in production, use Redis or database)
active_threads = {}


async def trigger_langgraph(query: str, file_path: str = None, filename: str = None, thread_id: str = "1"):

    thread = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "query": query,
        "file_dir": UPLOAD_DIR,
        "file_name": filename or "",
        "extracted_text_dir": EXTRACTED_CONTENT_DIR,
        "file_path": file_path or "",
        "extracted_text_path": "",
        "extraction_method": "",
        "extraction_status": "",
        "doc_text": "",
        "route": "",
        "orchestrator_plan": {},
        "product_data": {},
        "products_info": {}  # Add this for the interrupt node
    }

    final_state = None
    interrupt_data = None
    
    for node in graph.stream(initial_state, thread, stream_mode="updates"):
        if "__interrupt__" in node:
            print("Interrupt received:", node["__interrupt__"])
            raw_interrupt = node["__interrupt__"]

            # Extract the actual interrupt data from the tuple/object structure
            if isinstance(raw_interrupt, tuple) and len(raw_interrupt) > 0:
                interrupt_obj = raw_interrupt[0]
                if hasattr(interrupt_obj, 'value'):
                    interrupt_data = interrupt_obj.value
                else:
                    interrupt_data = interrupt_obj
            else:
                interrupt_data = raw_interrupt

            # Store the current state for resumption
            active_threads[thread_id] = {
                "state": final_state,
                "interrupt": interrupt_data,
                "query": query
            }
            # break
        else:
            print("State update:", node)
            final_state = node   # keep overwriting → last iteration = final state

    if interrupt_data:
        return {
            "interrupt": interrupt_data,
            "thread_id": thread_id,
            "query": query
        }


    # No interrupt - return final results
    product_data = final_state.get("product_data", None) if final_state else None

    return {
        "message": "Graph executed successfully",
        "query": query,
        "document_path": file_path,
        "product_data": product_data,
    }

async def resume_langgraph(thread_id: str, verified_products_info: dict):
    """Resume the graph execution after user verification."""
    
    if thread_id not in active_threads:
        raise ValueError(f"No active thread found for thread_id: {thread_id}")
    
    thread = {"configurable": {"thread_id": thread_id}}
    thread_data = active_threads[thread_id]
    
    # # Update the graph state with verified products
    # graph.update_state(thread, {"products_info": verified_products_info})
    from pprint import pprint
    print("Verified_products:", verified_products_info)
    
    final_state = None
    
    # Continue execution from where it left off
    for node in graph.stream(
        Command(resume=verified_products_info),
        thread, 
        stream_mode="values"
        ):
        if "__interrupt__" in node:
            print("Another interrupt received:", node["__interrupt__"])
            # Handle multiple interrupts if needed
            interrupt_data = node["__interrupt__"]
            active_threads[thread_id]["interrupt"] = interrupt_data
            return {
                "interrupt": interrupt_data,
                "thread_id": thread_id,
                "query": thread_data["query"]
            }
        else:
            print("State update:", node)
            final_state = node
    
    # Clean up the thread data
    query = thread_data["query"]
    del active_threads[thread_id]
    
    # Return final results
    product_data = final_state.get("product_data", None) if final_state else None
    
    return {
        "message": "Graph resumed and completed successfully",
        "query": query,
        "product_data": product_data,
    }
