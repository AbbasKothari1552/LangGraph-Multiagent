from fastapi import FastAPI, File, Form, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import shutil
import os
import sys
import json

from app.langgraph_runner import trigger_langgraph, resume_langgraph


from app.core.config import UPLOAD_DIR

app = FastAPI()

# Templates setup
templates = Jinja2Templates(directory="app/templates")

# Ensure upload folder exists
os.makedirs("upload_docs", exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    """Serve the main query form page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/run-graph", response_class=HTMLResponse)
async def run_graph(
    request: Request,
    query: str = Form(...),
    document: UploadFile = File(None)
):
    """Run the LangGraph and display results as product tables."""
    try:
        file_path = None
        filename = None

        # Save uploaded file if provided
        if document and document.filename:
            filename = document.filename
            file_path = os.path.join(UPLOAD_DIR, filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(document.file, buffer)

        # Call your LangGraph execution
        result = await trigger_langgraph(query, file_path, filename)

        # Check if there's an interrupt
        if result.get("interrupt"):
            interrupt_data = result["interrupt"]
            return templates.TemplateResponse(
                "interrupt.html",
                {
                    "request": request,
                    "query": query,
                    "interrupt_message": interrupt_data.get("message", ""),
                    "products_info": interrupt_data.get("product_info", {}),
                    "thread_id": result.get("thread_id", "1")
                }
            )

        # No interrupt - show results
        product_data = result.get("product_data", {})

        return templates.TemplateResponse(
            "products.html",
            {
                "request": request,
                "query": query,
                "product_data": product_data
            }
        )

    except Exception as e:
        return HTMLResponse(f"<h3>Error: {e}</h3>", status_code=500)
    

@app.post("/resume-graph")
async def resume_graph_endpoint(
    request: Request,
    thread_id: str = Form(...),
    verified_products: str = Form(...)  # JSON string of verified products
):
    """Resume the graph after user verification."""
    try:
        # Parse the verified products JSON
        products_info = json.loads(verified_products)
        
        # Resume the graph with verified data
        result = await resume_langgraph(thread_id, products_info)
        
        # Return the final results
        product_data = result.get("product_data", {})
        return templates.TemplateResponse(
            "products.html",
            {
                "request": request,
                "query": result.get("query", ""),
                "product_data": product_data
            }
        )
        
    except Exception as e:
        return HTMLResponse(f"<h3>Error resuming graph: {e}</h3>", status_code=500)
