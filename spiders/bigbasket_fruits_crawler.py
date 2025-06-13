from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager

def scroll_to_bottom(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def scrape_products(driver):
    time.sleep(2)
    product_cards = driver.find_elements(By.CSS_SELECTOR, "div[class*='SKUDeck']")

    data = []
    for card in product_cards:
        try:
            # Product link
            a_tag = card.find_element(By.CSS_SELECTOR, "a[target='_blank']")
            link = a_tag.get_attribute("href")

            # Product name (inside <h3>)
            name = a_tag.find_element(By.CSS_SELECTOR, "h3.text-darkOnyx-800").text.strip()

            # Product price
            price = card.find_element(By.CSS_SELECTOR, "div[class*='Pricing'] span").text.strip()

            data.append({
                "Name": name,
                "Price": price,
                "Link": link,
                "Delivery Time": "Based on pincode 400020"  # Optional: dynamic scraping
            })
        except Exception as e:
            continue

    print(f"✅ Total products scraped: {len(data)}")
    return data

def main():
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Step 1: Go to main BigBasket homepage first to set pincode cookie
    driver.get("https://www.bigbasket.com/")
    time.sleep(5)

    # Set pincode cookie manually (based on your pincode: 400020 - Mumbai)
    driver.add_cookie({
        'name': 'bb_location',
        'value': '{"pincode":"400020","city":"Mumbai","type":"pincode","locality":"Chowpatty","area":"Mumbai","isAvailable":true}',
        'domain': '.bigbasket.com'
    })

    # Step 2: Now go to fruits & vegetables page
    driver.get("https://www.bigbasket.com/pc/fruits-vegetables/")
    time.sleep(8)

    scroll_to_bottom(driver)

    # Step 3: Scrape data
    scraped_data = scrape_products(driver)
    driver.quit()

    # Save to CSV
    df = pd.DataFrame(scraped_data)
    df.to_csv("bigbasket_products.csv", index=False)
    print("📁 Data saved to bigbasket_products.csv")

if __name__ == "__main__":
    main()
