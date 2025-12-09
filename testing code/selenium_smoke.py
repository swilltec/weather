import os
import sys

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def build_driver(headless: bool) -> webdriver.Chrome:
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1400,900")
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )


def toggle_theme(driver: webdriver.Chrome, wait: WebDriverWait):
    initial = driver.execute_script("return document.documentElement.className")
    toggle = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//span[text()='Toggle theme']/.."))
    )
    toggle.click()
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return document.documentElement.className")
        != initial
    )
    toggle.click()
    WebDriverWait(driver, 10).until(
        lambda d: initial in d.execute_script("return document.documentElement.className")
    )


def run_smoke():
    base_url = os.getenv("BASE_URL", "http://localhost:5173/")
    test_city = os.getenv("TEST_CITY", "London")
    headless = os.getenv("HEADLESS", "1").lower() not in {"0", "false", "no"}

    driver = build_driver(headless=headless)
    wait = WebDriverWait(driver, 30)

    try:
        driver.get(base_url)

        search_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(., 'Search cities...')]")
            )
        )
        search_button.click()

        search_input = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//input[@placeholder='Search cities...']")
            )
        )
        search_input.clear()
        search_input.send_keys(test_city)

        suggestion = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    f"//div[@role='option' and contains(normalize-space(.), '{test_city}')]",
                )
            )
        )
        suggestion.click()

        wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, f"//h1[contains(., '{test_city}')]")
            )
        )

        favorite_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[.//svg[@data-lucide='star']]")
            )
        )
        favorite_button.click()

        logo_link = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "header a[href='/']"))
        )
        logo_link.click()

        wait.until(EC.visibility_of_element_located((By.XPATH, "//h1[text()='Favorites']")))
        wait.until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    f"//h1[text()='Favorites']/following::*[contains(., '{test_city}')][1]",
                )
            )
        )

        remove_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//h1[text()='Favorites']/following::button[.//svg[@data-lucide='x']][1]")
            )
        )
        remove_button.click()
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located(
                (
                    By.XPATH,
                    f"//h1[text()='Favorites']/following::*[contains(., '{test_city}')]",
                )
            )
        )

        toggle_theme(driver, wait)
        print("✅ Selenium smoke test completed successfully.")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"❌ Selenium smoke test failed: {exc}")
        return 1
    finally:
        driver.quit()


if __name__ == "__main__":
    sys.exit(run_smoke())
