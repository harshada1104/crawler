from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time, csv



def init_driver():
    options = Options()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def extract_products(driver):
    products = []
    try:
        product_cards = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.puis-card-container'))
        )
    except Exception as e:
        print(f"[⚠️] Failed to locate product cards: {e}")
        return products  # return empty list to skip

    for card in product_cards:
        try:
            name = card.find_element(By.CSS_SELECTOR, 'div[data-cy="title-recipe"] span').text.strip()
        except:
            name = "Not Found"

        try:
            price = card.find_element(By.CSS_SELECTOR, 'span.a-price').text.strip()
        except:
            price = "Not Found"

        try:
            delivery = card.find_element(By.CSS_SELECTOR, 'div[data-cy="delivery-recipe"]').text.strip()
        except:
            delivery = "Not Found"

        try:
            link = card.find_element(By.CSS_SELECTOR, 'a.a-link-normal').get_attribute("href")
            product_url = link if link.startswith("http") else "https://www.amazon.in" + link
        except:
            product_url = "Not Found"

        products.append({
            "name": name,
            "price": price,
            "delivery_time": delivery,
            "product_url": product_url
        })

    return products

def go_to_next_page(driver):
    try:
        next_btn = driver.find_element(By.CSS_SELECTOR, 'a.s-pagination-next')
        if 's-pagination-disabled' in next_btn.get_attribute('class'):
            return False
        driver.execute_script("arguments[0].scrollIntoView();", next_btn)
        time.sleep(1)
        next_btn.click()
        return True
    except:
        return False

def scrape_all_pages(url, output_file="amazon_scraped6.csv"):
    driver = init_driver()
    driver.get(url)
    all_products = []

    page = 1
    while True:
        print(f"\n[🔎] Scraping page {page}...")
        products = extract_products(driver)
        all_products.extend(products)
        print(f"[✓] Found {len(products)} products on page {page}.")

        user_input = input("[⏸] Press Enter to continue to next page, or type 'q' to quit: ")
        if user_input.strip().lower() == 'q':
            print("[🛑] Scraping stopped by user.")
            break

        if not go_to_next_page(driver):
            print("[⛔] No more pages found.")
            break

        page += 1
        time.sleep(2)

    driver.quit()

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "price", "delivery_time", "product_url"])
        writer.writeheader()
        writer.writerows(all_products)

    print(f"\n[💾] Saved {len(all_products)} total products to {output_file}")

if __name__ == "__main__":
    scrape_all_pages("https://www.amazon.in/s?i=beauty&rh=n%3A1355016031%2Cn%3A9851597031&s=popularity-rank&dc&fs=true&ds=v1%3Ah%2BTSmQmCyW10tHD%2Fg4BVzBhNiJJ0a4Mc%2FroUpOX0AEg&qid=1751354257&rnid=1355016031&xpid=e1TIk19Z0K52L&ref=sr_nr_n_3")
