from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time

def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")  # allow user to scroll manually
    # Do NOT use headless here
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def scrape_while_user_scrolls(url: str, output_file: str = "zepto_user_scroll.csv"):
    driver = init_driver()
    driver.get(url)
    print(f"[✓] Opened: {url}")
    print("[*] Start scrolling manually. Scraping will begin...")

    seen_urls = set()
    scraped_data = []
    unchanged_count = 0

    try:
        while True:
            product_cards = driver.find_elements(By.CSS_SELECTOR, 'a[data-testid="product-card"]')
            print(f"[+] Currently loaded products: {len(product_cards)}")

            new_items = 0
            for card in product_cards:
                try:
                    url = card.get_attribute("href").strip()
                    if url in seen_urls:
                        continue

                    name = card.find_element(By.CSS_SELECTOR, 'img[data-testid="product-card-image"]').get_attribute("alt").strip()
                    try:
                        price = card.find_element(By.CSS_SELECTOR, 'span[data-testid="product-price"]').text.strip()
                    except:
                        price = "Not Found"

                    scraped_data.append({
                        "name": name,
                        "price": price,
                        "url": url
                    })
                    seen_urls.add(url)
                    new_items += 1

                except Exception as e:
                    print("[-] Skipping one item due to error:", e)

            if new_items == 0:
                unchanged_count += 1
                if unchanged_count >= 5:  # No new data for 5 checks (i.e. ~15 seconds)
                    print("[✓] No more new items detected. Stopping.")
                    break
            else:
                unchanged_count = 0

            time.sleep(3)  # wait before checking again

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

# Run it
if __name__ == "__main__":
    scrape_while_user_scrolls("https://www.zeptonow.com/cn/fruits-vegetables/all/cid/64374cfe-d06f-4a01-898e-c07c46462c36/scid/e78a8422-5f20-4e4b-9a9f-22a0e53962e3")
