import hashlib
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

# Constants for rate limiting
REQUESTS_PER_MINUTE = 10
MIN_INTERVAL_BETWEEN_REQUESTS = 60 / REQUESTS_PER_MINUTE

# Global variables for tracking request times
last_request_time = 0
lock = threading.Lock()


def get_collection_name(url: str) -> str:
    # Generate a valid Milvus collection name based on the URL
    return hashlib.md5(url.encode("utf-8")).hexdigest()


def wait_for_next_request() -> None:
    """
    Ensures the minimum interval between requests is maintained to respect rate limits.
    """
    global last_request_time
    with lock:
        current_time = time.time()
        time_since_last_request = current_time - last_request_time
        if time_since_last_request < MIN_INTERVAL_BETWEEN_REQUESTS:
            wait_time = MIN_INTERVAL_BETWEEN_REQUESTS - time_since_last_request
            time.sleep(wait_time)
        last_request_time = time.time()


def scrape_website(base_url: str, robots_checker: RobotsTxtChecker) -> List[str]:
    """
    Scrapes a website's content while respecting its robots.txt restrictions and rate limits.

    Args:
        base_url (str): The base URL of the website to scrape.
        robots_checker (RobotsTxtChecker): An instance of RobotsTxtChecker to verify scraping permissions.

    Returns:
        List[str]: A list of text content extracted from <p> tags on the website, or a message if scraping is disallowed.
    """
    try:
        # Fetch and check robots.txt rules
        robots_checker.fetch()
        if not robots_checker.is_allowed():
            return [robots_checker.content]

        # Ensure the minimum interval between requests is maintained
        wait_for_next_request()

        # Set up headless Chrome WebDriver options
        options = Options()
        options.headless = False

        # Initialize WebDriver
        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()), options=options
        )

        # Fetch the page
        driver.get(base_url)
        time.sleep(10)  # Allow some time for the page to load

        # Parse the page source with BeautifulSoup
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
