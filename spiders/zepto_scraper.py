from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import random


def scrape_zepto(product_query: str, output_file: str = "zepto_output.csv"):
    # Setup Chrome options
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920x1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    )

    # Initialize WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Format search query and open URL
    query = product_query.replace(" ", "%20")
    url = f"https://www.zeptonow.com/search?query={query}"
    print(f"[+] Searching: {url}")
    driver.get(url)

    # Wait for product cards to appear
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[data-testid="product-card"]'))
        )
    except Exception as e:
        print("[!] Timeout waiting for products to load:", e)
        driver.quit()
        return

    # Scrape product data
    product_cards = driver.find_elements(By.CSS_SELECTOR, 'a[data-testid="product-card"]')
    results = []

    for card in product_cards:
        try:
            name = card.find_element(By.CSS_SELECTOR, 'img[data-testid="product-card-image"]').get_attribute("alt").strip()
            url = card.get_attribute("href").strip()

            try:
                price = card.find_element(By.CSS_SELECTOR, 'span[data-testid="product-price"]').text.strip()
            except:
                price = "Not Found"

            results.append({
                "name": name,
                "price": price,
                "url": url,
            })
        except Exception as e:
            print("[-] Skipping a product due to error:", e)
            continue

    # Export to CSV
    if results:
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "price", "url"])
            writer.writeheader()
            writer.writerows(results)
        print(f"[✓] Scraped {len(results)} products from Zepto.\nSaved to: {output_file}")
    else:
        print("[!] No products found or extracted. CSV file not created.")

    driver.quit()


# Run the scraper with hardcoded query
if __name__ == "__main__":
    scrape_zepto("powder")  # Example query
