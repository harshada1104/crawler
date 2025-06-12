import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def get_driver():
    options = Options()
    # TEMP: Disable headless for debugging
    # options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--enable-unsafe-swiftshader")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """
    })

    return driver


def scrape_from_zepto(product_name: str):
    print("\n[1] Searching on Zepto...")
    driver = get_driver()
    results = []
    try:
        query = product_name.replace(" ", "%20")
        url = f"https://www.zeptonow.com/search?query={query}"
        driver.get(url)
        print(f"Loaded URL: {url}")

        WebDriverWait(driver, 15).until(lambda d: d.execute_script("return document.readyState") == "complete")
        time.sleep(3)

        product_cards = driver.find_elements(By.CSS_SELECTOR, "a[data-testid='product-card']")
        print(f"Found {len(product_cards)} product cards")

        for card in product_cards:
            try:
                name = card.find_element(By.CSS_SELECTOR, 'img[data-testid="product-card-image"]').get_attribute("alt").strip()
                url = card.get_attribute("href").strip()

                try:
                    price = card.find_element(By.CSS_SELECTOR, 'span[data-testid="product-price"]').text.strip()
                except:
                    price = "Not Found"

                results.append({
                    "source": "Zepto",
                    "name": name,
                    "price": price,
                    "url": url,
                })
            except Exception as e:
                print("[-] Skipping a product due to error:", e)
                continue

        if not results:
            print("[!] Product not found on Zepto.")
            return None
        return results[0]  # Return the first result for consistency with swiggy
    except Exception as e:
        print("[Zepto Error]", e)
        return None
    finally:
        driver.quit()

   

def scrape_from_swiggy(product_name: str):
    print("\n[2] Searching on Swiggy Instamart...")
    driver = get_driver()
    try:
        query = product_name.replace(" ", "%20")
        url = f"https://www.swiggy.com/instamart/search?custom_back=true&query={query}"
        driver.get(url)
        print(f"Loaded URL: {url}")

        WebDriverWait(driver, 15).until(lambda d: d.execute_script("return document.readyState") == "complete")
        time.sleep(3)

        product_cards = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="default_container_ux4"]')
        print(f"Found {len(product_cards)} product cards")

        for card in product_cards:
            try:
                # Look for the role="button" container
                button_elem = card.find_element(By.CSS_SELECTOR, 'div[role="button"]')

                # Find all divs inside it and filter those with visible text
                divs = button_elem.find_elements(By.TAG_NAME, "div")
                for div in divs:
                    name = div.text.strip()
                    if name and product_name.lower().replace(" ", "") in name.lower().replace(" ", ""):
                        print(f"[✓] Found on Swiggy Instamart: {name}")
                        return {
                            "source": "Swiggy Instamart",
                            "name": name,
                            "price": "Not Found",
                            "url": driver.current_url,
                        }
            except Exception as e:
                print("[Swiggy Card Error]", e)
                continue

        print("[!] Product not found on Swiggy Instamart.")
        return None
    except Exception as e:
        print("[Swiggy Instamart Error]", e)
        return None
    finally:
        driver.quit()


def save_to_csv(results, filename="combined_scraped_results.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["source", "name", "price", "url"])
        writer.writeheader()
        writer.writerows(results)
    print(f"\n[✓] Saved results to: {filename}")


if __name__ == "__main__":
    product = "amul"
    all_results = []

    zepto_result = scrape_from_zepto(product)
    if zepto_result:
        all_results.append(zepto_result)

    swiggy_result = scrape_from_swiggy(product)
    if swiggy_result:
        all_results.append(swiggy_result)

    if all_results:
        save_to_csv(all_results)
    else:
        print("\n[!] Product not found on either Zepto or Swiggy Instamart.")
