from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time

def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def scrape_while_user_scrolls(url: str, output_file: str = "swiggy_user_scroll.csv"):
    driver = init_driver()
    driver.get(url)
    print(f"[✓] Opened: {url}")
    print("[*] Scroll the page manually. Scraping begins...")

    seen_names = set()
    scraped_data = []
    unchanged_count = 0

    try:
        while True:
            product_cards = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="ItemWidgetContainer"]')
            print(f"[+] Currently loaded products: {len(product_cards)}")

            new_items = 0
            for card in product_cards:
                try:
                    # Extract product name
                    name_elem = card.find_element(By.CSS_SELECTOR, 'div.novMV')
                    name = name_elem.text.strip()

                    if name in seen_names:
                        continue

                    # Attempt to extract item ID from nested elements
                    item_id = None
                    try:
                        # Find button or div that contains something unique
                        price_container = card.find_element(By.CSS_SELECTOR, 'div[data-testid="itemMRPPrice"]')
                        outer_html = price_container.get_attribute("outerHTML")

                        # Try to find an ID-like value (e.g., 8XDFK317E7) from the HTML string
                        import re
                        match = re.search(r'item/([A-Z0-9]+)', outer_html)
                        if match:
                            item_id = match.group(1)
                        else:
                            # Attempt fallback: look for any 10-char alphanumeric code
                            fallback_match = re.search(r'([A-Z0-9]{10,})', outer_html)
                            if fallback_match:
                                item_id = fallback_match.group(1)
                    except:
                        pass

                    # Construct item URL
                    if item_id:
                        item_url = f"https://www.swiggy.com/instamart/item/{item_id}?storeId=1382964"
                    else:
                        item_url = url  # fallback to main page

                    scraped_data.append({
                        "name": name,
                        "price": "Not Found",
                        "url": item_url
                    })
                    seen_names.add(name)
                    new_items += 1

                except Exception as e:
                    print("[-] Skipping one item due to error:", e)

            if new_items == 0:
                unchanged_count += 1
                if unchanged_count >= 5:
                    print("[✓] No more new items detected. Stopping.")
                    break
            else:
                unchanged_count = 0

            time.sleep(3)

    finally:
        driver.quit()

    # Save results
    if scraped_data:
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "price", "url"])
            writer.writeheader()
            writer.writerows(scraped_data)
        print(f"[✓] Saved {len(scraped_data)} products to: {output_file}")
    else:
        print("[!] No products scraped.")

# Run the scraper
if __name__ == "__main__":
    scrape_while_user_scrolls(
        "https://www.swiggy.com/instamart/category-listing?categoryName=Fresh+Vegetables&custom_back=true&filterId=6822eeeded32000001e25aa4&filterName=&offset=0&showAgeConsent=false&storeId=1382964&taxonomyType=Speciality+taxonomy+1"
    )
