from fastapi import FastAPI, File, Form, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import shutil
import os
import sys

from app.langgraph_runner import trigger_langgraph

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.config import UPLOAD_DIR

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

        # Extract product_data safely
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
