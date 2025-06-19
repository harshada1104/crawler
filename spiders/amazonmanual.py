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


def extract_products(driver):
    seen = set()
    products = []

    product_cards = driver.find_elements(By.CSS_SELECTOR, 'div[data-csa-c-item-type="asin"]')
    for card in product_cards:
        try:
            name = card.find_element(By.CSS_SELECTOR, 'a.a-link-normal span.a-color-base').text.strip()
            if not name or name in seen:
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
                delivery_time = card.find_element(By.CSS_SELECTOR, 'span.a-size-small.a-color-base').text
            except:
                delivery_time = "Not Found"

            # Product URL
            try:
                product_link = card.find_element(By.CSS_SELECTOR, 'a.a-link-normal').get_attribute("href")
                if product_link.startswith("http") and "amazon.in" in product_link:
                    product_url = product_link
                else:
                    product_url = "https://www.amazon.in" + product_link
            except:
                product_url = "Not Found"

            products.append({
                "name": name,
                "price": price,
                "delivery_time": delivery_time,
                "product_url": product_url
            })
            seen.add(name)

        except Exception as e:
            print("[-] Skipping a product due to:", e)

    return products


def scrape_amazon_fresh_manual(url, output_file="amazon_fresh_manual_scroll.csv"):
    driver = init_driver()
    driver.get(url)
    time.sleep(4)

    all_products = []

    # Let the user scroll manually
    print("[🟡] Please scroll through all products manually until you reach the end of the list.")
    input("[🔽] Press Enter here **after you're done scrolling**...")

    # Now scrape all visible products
    section_products = extract_products(driver)
    all_products.extend(section_products)
    print(f"[✓] Scraped {len(section_products)} products.")

    driver.quit()

    if all_products:
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "price", "delivery_time", "product_url"])
            writer.writeheader()
            writer.writerows(all_products)
        print(f"\n[✓] Total {len(all_products)} products saved to: {output_file}")
    else:
        print("[!] No products scraped.")


# Run the manual scroll scraper
if __name__ == "__main__":
    scrape_amazon_fresh_manual("https://www.amazon.in/alm/category/fresh/Oils-Ghee?almBrandId=ctnow&node=4859491031&ref=fs_dsk_sn_fs-nav-fs-oilghe-f0af8")
