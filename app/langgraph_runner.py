from app.core.config import UPLOAD_DIR, EXTRACTED_CONTENT_DIR
from app.workflow.main_workflow import graph

thread = {"configurable": {"thread_id": "1"}}


async def trigger_langgraph(query: str, file_path: str = None, filename: str = None):
    final_state = None
    
    for node in graph.stream(
        {
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
            "product_data": {},   # make sure product_data is part of state
        },
        thread,
        stream_mode="values"
    ):
        print(node)   # Debug: see full state emitted
        final_state = node   # keep overwriting → last iteration = final state

    # Now pull product_data out of final_state
    product_data = final_state.get("product_data", None) if final_state else None

    return {
        "message": "Graph executed successfully",
        "query": query,
        "document_path": file_path,
        "product_data": product_data,
    }
