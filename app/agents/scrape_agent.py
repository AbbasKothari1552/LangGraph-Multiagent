from app.state.scrape_subgraph_state import ScrapeSubGraphState
from app.tools.scraper_tool import instant_api_scrape

from app.core.logging_config import get_logger
logger = get_logger(__name__)



def scrape_agent(state: ScrapeSubGraphState) -> ScrapeSubGraphState:
    """
    Scrapes the urls using Instant API.
    """
    url = state.get("url", [])
    product_info = state.get("information", {})
    if not product_info or "search_query" not in product_info:
        raise ValueError("Product or search_query missing in state")
    
    # get fields
    fields = product_info["fields"]
    product_name = product_info["name"]

    product_data = []

    try: 
        print(f"Scraping URL: {url}")
        raw_response = instant_api_scrape(url, fields)

        try:
            scraped_data = raw_response.get("scrape", [])
        except:
             print("Null returned by instant api")
             return state

        if not scraped_data:
            print(f"No data scraped for URL: {url}")
            return state

        # add data dict into product_data
        for data in scraped_data:
            state["scraped_data"].append(data)
            # product_data.append(data)
        print("Scraped Data:")
        # pprint(scraped_data)
    
    except Exception as e:
            print(f"Error scraping data for {url}: {str(e)}")
            return state


    # product_data = []
    # for idx, url in enumerate(urls):
    #     try:
    #         print(f"{idx + 1} -> Scraping data for URL: {url}")
    #         raw_response = instant_api_scrape(url, fields)
    #         scraped_data = raw_response.get("scrape", [])
    #         if not scraped_data:
    #             print(f"No data scraped for URL: {url}")
    #             continue

    #         # add data dict into product_data
    #         for data in scraped_data:
    #             product_data.append(data)
    #         print("Scraped Data:")
    #         # pprint(scraped_data)

    #         # For saving API calls
    #         # *** Remove IT *** 
    #         # break
       
       
    #     except Exception as e:
    #         print(f"Error scraping data for {url}: {str(e)}")
    

    # if product_data:
    #     state["product_data"].setdefault(product_name, [])
    #     state["product_data"][product_name].extend(product_data)
    #     print(f"Added {len(product_data)} records to state for schema '{product_name}'.")
    # else:
    #     print(f"No valid data collected for schema '{product_name}'.")

    return state

