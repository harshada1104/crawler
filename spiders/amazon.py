from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv


def init_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def slow_auto_scroll(driver, pause_time=3.5, step=1000):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script(f"window.scrollBy(0, {step});")
        time.sleep(pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def scrape_amazon_fresh(url: str, output_file: str = "amazon_fresh_scraped.csv"):
    driver = init_driver()
    driver.get(url)
    print(f"[✓] Opened: {url}")

    print("[*] Scrolling to load all products...")
    slow_auto_scroll(driver)

    seen_names = set()
    scraped_data = []

    product_cards = driver.find_elements(By.CSS_SELECTOR, 'div[data-csa-c-item-type="asin"]')
    print(f"[+] Total product cards found: {len(product_cards)}")

    for card in product_cards:
        try:
            # Name
            name_elem = card.find_element(By.CSS_SELECTOR, 'a.a-link-normal > span.a-color-base')
            name = name_elem.text.strip()

            if name in seen_names or name == "":
                continue

            # Price
            try:
                price_whole = card.find_element(By.CSS_SELECTOR, 'span.a-price-whole').text
                price_fraction = card.find_element(By.CSS_SELECTOR, 'span.a-price-fraction').text
                price = f"₹{price_whole}.{price_fraction}"
            except:
                price = "Not Found"

            # Delivery time
            try:
                delivery_elem = card.find_element(By.CSS_SELECTOR, 'div.a-row span.a-size-small.a-color-base')
                delivery_time = delivery_elem.text.strip()
            except:
                delivery_time = "Not Found"

            # Get real product link from <a> tag href
            try:
                product_anchor = card.find_element(By.CSS_SELECTOR, 'a.a-link-normal')
                product_url = product_anchor.get_attribute("href").split("?")[0]  # canonical link
            except:
                product_url = "Not Found"

            scraped_data.append({
                "name": name,
                "price": price,
                "delivery_time": delivery_time,
                "product_url": product_url
            })

            seen_names.add(name)

        except Exception as e:
            print("[-] Skipping item due to error:", e)

    driver.quit()

    if scraped_data:
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "price", "delivery_time", "product_url"])
            writer.writeheader()
            writer.writerows(scraped_data)
        print(f"[✓] Saved {len(scraped_data)} products to: {output_file}")
    else:
        print("[!] No data scraped.")


# Run
if __name__ == "__main__":
    scrape_amazon_fresh(
        "https://www.amazon.in/alm/category/fresh/Oils-Ghee?almBrandId=ctnow&node=4859491031&ref=fs_dsk_sn_fs-nav-fs-oilghe-f0af8"
    )
