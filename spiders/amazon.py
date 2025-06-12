from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time

def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def scrape_amazon_fresh(url: str, output_file: str = "amazon_fresh_carousel.csv"):
    driver = init_driver()
    driver.get(url)
    print(f"[✓] Opened: {url}")
    print("[*] Scroll the page manually if needed. Scraping begins...")

    seen_names = set()
    scraped_data = []
    unchanged_count = 0

    try:
        while True:
            time.sleep(4)  # Let carousel load more items

            product_cards = driver.find_elements(By.CSS_SELECTOR, 'div[data-csa-c-item-type="asin"]')
            print(f"[+] Currently loaded products: {len(product_cards)}")

            new_items = 0
            for card in product_cards:
                try:
                    name_elem = card.find_element(By.CSS_SELECTOR, 'a.a-link-normal > span.a-color-base')
                    name = name_elem.text.strip()

                    if name in seen_names or name == "":
                        continue

                    # Price scraping
                    try:
                        price_whole = card.find_element(By.CSS_SELECTOR, 'span.a-price-whole').text
                        price_fraction = card.find_element(By.CSS_SELECTOR, 'span.a-price-fraction').text
                        price = f"₹{price_whole}.{price_fraction}"
                    except:
                        price = "Not Found"

                    # Delivery time scraping (optional element)
               
                    try:
                        delivery_elem = card.find_element(By.CSS_SELECTOR, 'div.a-row span.a-size-small.a-color-base')
                        delivery_time = delivery_elem.text.strip()
                    except:
                        delivery_time = "Not Found"

                    scraped_data.append({
                        "name": name,
                        "price": price,
                        "delivery_time": delivery_time,
                        "url": driver.current_url
                    })
                    seen_names.add(name)
                    new_items += 1

                except Exception as e:
                    print("[-] Skipping item due to error:", e)

            if new_items == 0:
                unchanged_count += 1
                if unchanged_count >= 3:
                    print("[✓] No more new items detected. Stopping.")
                    break
            else:
                unchanged_count = 0

    finally:
        driver.quit()

    # Save results
    if scraped_data:
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "price", "delivery_time", "url"])
            writer.writeheader()
            writer.writerows(scraped_data)
        print(f"[✓] Saved {len(scraped_data)} products to: {output_file}")
    else:
        print("[!] No products scraped.")

# Run the scraper
if __name__ == "__main__":
    scrape_amazon_fresh(
        "https://www.amazon.in/alm/category/fresh/Fresh-Fruits-Vegetables?almBrandId=ctnow&node=4859496031&ref=fs_dsk_sn_fruitsVegetables-9679e"
    )
