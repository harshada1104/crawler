from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

def init_driver():
    options = Options()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def set_pincode(driver, pincode="400053"):
    try:
        print(f"[*] Setting pincode to {pincode}...")
        driver.get("https://www.zeptonow.com/")
        
        # Click the address/location button
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-haspopup="dialog"]'))
        ).click()

        # Wait for the address input box to show up
        input_box = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[placeholder*="Search a new address"]'))
        )

        input_box.clear()
        input_box.send_keys(pincode)
        input_box.send_keys(Keys.ENTER)

        # Wait until address changes or overlay disappears
        WebDriverWait(driver, 15).until(
            EC.invisibility_of_element((By.CSS_SELECTOR, '[data-testid="address-modal"]'))
        )

        print(f"[✓] Location set to pincode {pincode}")

    except Exception as e:
        print(f"[!] Failed to set pincode: {e}")

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

def scrape_zepto_products(driver, pincode="400053"):
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
                price = card.find_element(By.CSS_SELECTOR, 'h4[data-testid="product-card-price"]').text.strip()
            except:
                price = "Not Found"

            scraped_data.append({
                "Name": name,
                "Price": price,
                "Link": url,
                "Pincode": pincode
            })

            seen_urls.add(url)

        except Exception as e:
            print("[-] Skipping item due to error:", e)

    print(f"✅ Total products scraped: {len(scraped_data)}")
    return scraped_data

def main():
    driver = init_driver()
    pincode = "400053"

    set_pincode(driver, pincode)

    # 💡 Use any valid product category URL below
    url = "https://www.zeptonow.com/cn/atta-rice-oil-dals/atta-rice-oil-dals/cid/2f7190d0-7c40-458b-b450-9a1006db3d95/scid/84f270cf-ae95-4d61-a556-b35b563fb947"
    print(f"[✓] Opening category page: {url}")
    driver.get(url)

    print("[*] Slowly scrolling to load all products...")
    slow_auto_scroll(driver, pause_time=5.5, step=500)

    scraped_data = scrape_zepto_products(driver, pincode)
    driver.quit()

    df = pd.DataFrame(scraped_data)
    df.to_csv("zepto_products.csv", index=False)
    print("📁 Data saved to zepto_products.csv")

if __name__ == "__main__":
    main()
