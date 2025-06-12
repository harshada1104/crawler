import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time


def scrape_from_swiggy(product_name: str):
    print("\n[2] Searching on Swiggy Instamart...")

    # Setup headless Chrome options
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

    # Initialize driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        query = product_name.replace(" ", "%20")
        url = f"https://www.swiggy.com/instamart/search?custom_back=true&query={query}"
        driver.get(url)
        print(f"Loaded URL: {url}")

        # Wait for product tiles to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="default_container_ux4"]'))
        )

        product_cards = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="default_container_ux4"]')
        print(f"Found {len(product_cards)} product cards")

        for card in product_cards:
            try:
                name_elem = card.find_element(By.CSS_SELECTOR, "div.sc-aXZVg kyEzVU SF1nE")
                name = name_elem.text.strip()

                if product_name.lower() in name.lower():
                    print(f"[✓] Found on Swiggy Instamart: {name}")
                    result = {
                        "name": name,
                        "price": "Not Found",  # Placeholder if price is not available
                        "url": driver.current_url
                    }
                    return result

            except Exception as inner_error:
                continue

        print("[!] Product not found on Swiggy Instamart.")
        return None

    except Exception as e:
        print("[Swiggy Instamart Error]", e)
        return None

    finally:
        driver.quit()


def save_to_csv(data, filename='swiggy_results.csv'):
    if data:
        fieldnames = ['name', 'price', 'url']
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(data)
        print(f"[✓] Data saved to '{filename}'")
    else:
        print("[!] No data to write to CSV")


# Example usage
if __name__ == "__main__":
    result = scrape_from_swiggy("amul")
    if result:
        print("\n[✓] Scraped Result:\n", result)
        save_to_csv(result)
