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


def slow_auto_scroll(driver, pause_time=2.5, step=1000):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script(f"window.scrollBy(0, {step});")
        time.sleep(pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


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


def scrape_amazon_fresh(url, output_file="amazon_fresh_final.csv"):
    driver = init_driver()
    driver.get(url)
    time.sleep(4)

    all_products = []

    # Initial scroll and collect the total number of "See All" links
    slow_auto_scroll(driver, pause_time=3)
    total_links = driver.find_elements(By.CSS_SELECTOR, 'a.a-size-base.a-spacing-top-mini.a-link-emphasis')
    total_sections = len(total_links)
    print(f"[+] Found {total_sections} 'See All' links")

    for idx in range(total_sections):
        try:
            # Re-fetch the links to avoid stale element error
            see_all_links = driver.find_elements(By.CSS_SELECTOR, 'a.a-size-base.a-spacing-top-mini.a-link-emphasis')
            if idx >= len(see_all_links):
                print(f"[!] Skipping index {idx} as it's no longer available.")
                continue

            link = see_all_links[idx]
            link_text = link.text.strip()

            print(f"\n[→] Processing section: {link_text}")

            driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", link)
            driver.execute_script("arguments[0].click();", link)
            time.sleep(4)

            slow_auto_scroll(driver, pause_time=3)
            section_products = extract_products(driver)
            all_products.extend(section_products)

            print(f"[✓] Scraped {len(section_products)} products from section: {link_text}")

            driver.back()
            time.sleep(4)
            slow_auto_scroll(driver, pause_time=3)

        except Exception as e:
            print(f"[!] Failed on section {idx + 1}: {e}")
            continue

    driver.quit()

    if all_products:
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "price", "delivery_time", "product_url"])
            writer.writeheader()
            writer.writerows(all_products)
        print(f"\n[✓] Total {len(all_products)} products saved to: {output_file}")
    else:
        print("[!] No products scraped.")


# Run the scraper
if __name__ == "__main__":
    scrape_amazon_fresh("https://www.amazon.in/alm/category/fresh/Oils-Ghee?almBrandId=ctnow&node=4859491031&ref=fs_dsk_sn_fs-nav-fs-oilghe-f0af8")
