from typing import Dict
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import requests
import os

from langsmith import traceable

from dotenv import load_dotenv
load_dotenv()


def scrape_url(url: str, use_playwright: bool = True, timeout: int = 30) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        )
    }

    try:
        if use_playwright:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()
                page.set_default_timeout(timeout * 1000)
                page.goto(url, wait_until="load")
                page.wait_for_timeout(3000)  # Let JS render
                content = page.content()
                browser.close()
        else:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            content = response.text

        # Parse text from HTML
        soup = BeautifulSoup(content, "html.parser")
        title = soup.title.string.strip() if soup.title else ""
        paragraphs = " ".join(p.get_text().strip() for p in soup.find_all("p"))
        return f"{title}\n{paragraphs}"

    except Exception as e:
        return f"Error: {str(e)}"


from web_extract_data import WebExtractClient

client = WebExtractClient(os.getenv("INSTANT_API_KEY"))

@traceable(name="InstantAPI_SCRAPE_Call")
def instant_api_scrape(url: str, fields: dict):

    try: 
        response = client.scrape(
            url = url,
            fields = [fields]
        )

        return response
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}


@traceable(name="InstantAPI_URL_Call")
def instant_api_url(url: list, description: str):
    print(f"Fetching link for url: {url}")
    
    try:
        links_resp = client.links(
        url= url,
        description= description
        )
    except Exception as e:
        print(f"An error occurred: {e}")
        
    print("Fetched.")

    return links_resp