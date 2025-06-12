from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time
import re

def init_driver():
    options = Options()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def get_product_id_via_click(driver, card):
    try:
        # Open product in new tab via Ctrl+Click (Command+Click on Mac)
        webdriver.ActionChains(driver).key_down(Keys.CONTROL).click(card).key_up(Keys.CONTROL).perform()
        time.sleep(3)

        # Switch to new tab
        driver.switch_to.window(driver.window_handles[-1])
        current_url = driver.current_url

        match = re.search(r'/item/([A-Z0-9]+)', current_url)
        product_id = match.group(1) if match else None

        # Close the tab and return to main
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return product_id, current_url if product_id else ("Not Found", "Not Found")

    except Exception as e:
        print("[-] Error getting product URL via click:", e)
        return "Not Found", "Not Found"

def scrape_swiggy_product_urls(url: str, output_file: str = "swiggy_click_extract.csv"):
    driver = init_driver()
    driver.get(url)
    print(f"[✓] Opened: {url}")
    print("[*] Please scroll down manually. Scraping begins...")

    seen = set()
    results = []
    unchanged = 0

    try:
        while True:
            cards = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="ItemWidgetContainer"]')
            print(f"[+] Currently loaded cards: {len(cards)}")

            new_count = 0
            for card in cards:
                try:
                    name_elem = card.find_element(By.CSS_SELECTOR, 'div.novMV')
                    name = name_elem.text.strip()

                    if name in seen:
                        continue

                    product_id, product_url = get_product_id_via_click(driver, card)

                    results.append({
                        "name": name,
                        "product_id": product_id,
                        "product_url": product_url
                    })

                    seen.add(name)
                    new_count += 1

                except Exception as e:
                    print("[-] Error processing card:", e)

            if new_count == 0:
                unchanged += 1
                if unchanged >= 3:
                    print("[✓] No more new items detected. Stopping.")
                    break
            else:
                unchanged = 0

            time.sleep(3)

    finally:
        driver.quit()

    # Save data
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "product_id", "product_url"])
        writer.writeheader()
        writer.writerows(results)

    print(f"[✓] Saved {len(results)} products to: {output_file}")

# Run it
if __name__ == "__main__":
    scrape_swiggy_product_urls(
        "https://www.swiggy.com/instamart/category-listing?categoryName=Fresh+Vegetables&storeId=1382964"
    )
