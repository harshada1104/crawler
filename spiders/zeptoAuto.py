from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

def init_driver():
    options = Options()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def slow_auto_scroll(driver, pause_time=2, step=1000, max_unchanged_scrolls=5):
    last_height = driver.execute_script("return document.body.scrollHeight")
    unchanged_scrolls = 0
    scroll_position = 0

    while True:
        scroll_position += step
        driver.execute_script(f"window.scrollTo(0, {scroll_position});")
        time.sleep(pause_time)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            unchanged_scrolls += 1
            if unchanged_scrolls >= max_unchanged_scrolls:
                break
        else:
            unchanged_scrolls = 0
            last_height = new_height

def scrape_zepto_products(driver):
    seen_urls = set()
    scraped_data = []

    product_cards = driver.find_elements(By.CSS_SELECTOR, 'a[data-testid="product-card"]')
    print(f"[+] Total product cards loaded: {len(product_cards)}")

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
                "Name": name,
                "Price": price,
                "Link": url,
               
            })

            seen_urls.add(url)

        except Exception as e:
            print("[-] Skipping item due to error:", e)

    print(f"✅ Total products scraped: {len(scraped_data)}")
    return scraped_data

def main():
    driver = init_driver()

    url = "https://www.zeptonow.com/cn/fruits-vegetables/all/cid/64374cfe-d06f-4a01-898e-c07c46462c36/scid/e78a8422-5f20-4e4b-9a9f-22a0e53962e3"
    driver.get(url)
    print(f"[✓] Opened Zepto page: {url}")

    print("[*] Slowly scrolling through the page to load all products...")
    slow_auto_scroll(driver, pause_time=5.5, step=500)

    scraped_data = scrape_zepto_products(driver)
    driver.quit()

    df = pd.DataFrame(scraped_data)
    df.to_csv("zepto_products.csv", index=False)
    print("📁 Data saved to zepto_products.csv")

if __name__ == "__main__":
    main()
