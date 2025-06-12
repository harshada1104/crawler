from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time


def create_driver():
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
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def scrape_from_zepto(product_name):
    try:
        driver = create_driver()
        query = product_name.replace(" ", "%20")
        url = f"https://www.zeptonow.com/search?query={query}"
        driver.get(url)

        WebDriverWait(driver, 15).until(
            lambda d: d.find_elements(By.CSS_SELECTOR, 'a[data-testid="product-card"]') or
                      "no products found" in d.page_source.lower()
        )

        cards = driver.find_elements(By.CSS_SELECTOR, 'a[data-testid="product-card"]')
        for card in cards:
            try:
                name = card.find_element(By.CSS_SELECTOR, 'img[data-testid="product-card-image"]').get_attribute("alt").strip()
                if name.lower() == product_name.lower():
                    try:
                        price = card.find_element(By.CSS_SELECTOR, 'span[data-testid="product-price"]').text.strip()
                    except:
                        price = "Not Found"
                    link = card.get_attribute("href").strip()
                    return {"name": name, "price": price, "url": link}
            except:
                continue
    except Exception as e:
        print("[Zepto Error]", e)
    finally:
        driver.quit()
    return None


def scrape_from_swiggy(product_name):
    try:
        driver = create_driver()
        query = product_name.replace(" ", "%20")
        url = f"https://www.swiggy.com/instamart/search?query={query}"
        driver.get(url)

        # Wait for products or error message
        WebDriverWait(driver, 15).until(
            lambda d: d.find_elements(By.CSS_SELECTOR, 'div._3Yew7') or "no products found" in d.page_source.lower()
        )

        product_blocks = driver.find_elements(By.CSS_SELECTOR, 'div._3Yew7')
        for block in product_blocks:
            try:
                name_elem = block.find_element(By.CSS_SELECTOR, 'div._1RPOp')
                name = name_elem.text.strip()
                if name.lower() == product_name.lower():
                    try:
                        price = block.find_element(By.CSS_SELECTOR, 'div._1kMS').text.strip()
                    except:
                        price = "Not Found"
                    return {
                        "name": name,
                        "price": price,
                        "url": url  # Instamart doesn't offer individual product URLs
                    }
            except:
                continue
    except Exception as e:
        print("[Swiggy Instamart Error]", e)
    finally:
        driver.quit()
    return None


def save_to_csv(results, filename="product_comparison.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "price", "url", "source"])
        writer.writeheader()
        writer.writerows(results)


def scrape_from_zepto(product_name):
    try:
        driver = create_driver()
        query = product_name.replace(" ", "%20")
        url = f"https://www.zeptonow.com/search?query={query}"
        driver.get(url)
        print(f"Loaded URL: {url}")

        WebDriverWait(driver, 15).until(
            lambda d: d.find_elements(By.CSS_SELECTOR, 'a[data-testid="product-card"]') or
                      "no products found" in d.page_source.lower()
        )

        cards = driver.find_elements(By.CSS_SELECTOR, 'a[data-testid="product-card"]')
        print(f"Found {len(cards)} product cards")

        for card in cards:
            try:
                name = card.find_element(By.CSS_SELECTOR, 'img[data-testid="product-card-image"]').get_attribute("alt").strip()
                print("Found product:", name)
                if product_name.lower() in name.lower():  # <- Partial match
                    try:
                        price = card.find_element(By.CSS_SELECTOR, 'span[data-testid="product-price"]').text.strip()
                    except:
                        price = "Not Found"
                    link = card.get_attribute("href").strip()
                    return {"name": name, "price": price, "url": link}
            except Exception as inner_e:
                print("Error reading card:", inner_e)
                continue
    except Exception as e:
        print("[Zepto Error]", e)
        import traceback; traceback.print_exc()
    finally:
        driver.quit()
    return None
def scrape_all_sources(product_query):
    results = []

    # Scrape from Zepto
    zepto_result = scrape_from_zepto(product_query)
    if zepto_result:
        zepto_result["source"] = "Zepto"
        results.append(zepto_result)
        print(f"[✓] Found on Zepto: {zepto_result['name']} - {zepto_result['price']}")
# Run the combined scraper
if __name__ == "__main__":
    product_query = "amul"  # <-- You can replace this
    scrape_all_sources(product_query)
