from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.devtools import network
from selenium.webdriver.devtools import log
from webdriver_manager.chrome import ChromeDriverManager
import json, re, csv, time

def extract_product_ids_from_response(response_body):
    product_ids = set()
    try:
        data = json.loads(response_body)

        def find_ids(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k in ["productId", "itemCode", "code"] and isinstance(v, str) and len(v) >= 6:
                        product_ids.add(v)
                    else:
                        find_ids(v)
            elif isinstance(obj, list):
                for i in obj:
                    find_ids(i)
        find_ids(data)
    except Exception:
        pass
    return product_ids

def scrape_product_ids_from_swiggy(category_url, store_id="1382964"):
    # Setup Chrome with DevTools
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Get DevTools session
    driver.execute_cdp_cmd("Network.enable", {})

    product_ids = set()

    def handle_response(params):
        try:
            if "application/json" in params["response"]["mimeType"]:
                request_id = params["requestId"]
                body = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
                new_ids = extract_product_ids_from_response(body.get("body", ""))
                product_ids.update(new_ids)
        except Exception:
            pass

    # Attach listener
    driver.request_interceptor = None
    driver.response_interceptor = handle_response

    print("[+] Opening page...")
    driver.get(category_url)
    time.sleep(10)
    driver.quit()

    print(f"[✓] Found {len(product_ids)} product IDs")

    # Generate product URLs
    urls = [f"https://www.swiggy.com/instamart/item/{pid}?storeId={store_id}" for pid in product_ids]

    # Save to CSV
    with open("swiggy_product_urls.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["product_id", "url"])
        for pid, url in zip(product_ids, urls):
            writer.writerow([pid, url])

    print("[✓] Saved product URLs to swiggy_product_urls.csv")

# Run the function
scrape_product_ids_from_swiggy(
    "https://www.swiggy.com/instamart/category-listing?categoryName=Fresh%20Vegetables&storeId=1382964"
)
