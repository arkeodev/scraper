import threading
import time
from typing import List

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from scraper.scraping.robots import RobotsTxtChecker

REQUESTS_PER_MINUTE = 10
MIN_INTERVAL_BETWEEN_REQUESTS = 60 / REQUESTS_PER_MINUTE
last_request_time = 0
lock = threading.Lock()


def wait_for_next_request():
    global last_request_time
    with lock:
        current_time = time.time()
        time_since_last_request = current_time - last_request_time
        if time_since_last_request < MIN_INTERVAL_BETWEEN_REQUESTS:
            wait_time = MIN_INTERVAL_BETWEEN_REQUESTS - time_since_last_request
            time.sleep(wait_time)
        last_request_time = time.time()


def scrape_website(base_url: str, robots_checker: RobotsTxtChecker) -> List[str]:
    robots_checker.fetch()
    if not robots_checker.is_allowed():
        return [robots_checker.content]

    try:
        wait_for_next_request()

        options = Options()
        options.headless = True

        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()), options=options
        )

        driver.get(base_url)
        time.sleep(3)

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        texts = [p.get_text(strip=True) for p in soup.find_all("p")]

    except WebDriverException as e:
        print(f"WebDriver error: {e}")
        texts = []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        texts = []
    finally:
        if "driver" in locals():
            driver.quit()

    return texts
