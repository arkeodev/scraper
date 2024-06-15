# scraper.py
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, List, Optional
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from scraper.config.config import ScraperConfig
from scraper.scraping.link_collector import LinkCollector
from scraper.scraping.robots import RobotsTxtChecker
from scraper.utility.utils import extract_readable_text


class WebScraper:
    """
    A class responsible for web scraping operations.
    """

    def __init__(
        self,
        base_url: str,
        config: ScraperConfig,
        robots_checker: Optional[RobotsTxtChecker] = None,
        driver: Optional[webdriver.Chrome] = None,
        parser: Optional[Callable] = None,
    ):
        self.base_url = base_url
        self.robots_checker = (
            robots_checker if robots_checker else RobotsTxtChecker(base_url)
        )
        self.driver = driver if driver else self._setup_driver()
        self.parser = parser if parser else BeautifulSoup
        self.config = config if config else ScraperConfig()
        self.documents: List[str] = []
        self.link_collector = LinkCollector(self.base_url, self.driver, self.parser)
        self.visited_urls = set()

    def _setup_driver(self) -> webdriver.Chrome:
        options = Options()
        options.headless = True
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        logging.info("Setting up Chrome WebDriver")
        return webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()), options=options
        )

    def scrape(self) -> List[str]:
        try:
            logging.info("Starting scraping process")
            self.robots_checker.fetch()
            logging.info("robots_checker.fetch() completed")
            links_to_scrape = self.link_collector.collect_all_links(
                self.config.page_load_timeout, self.config.page_load_sleep
            )
            logging.info(f"Collected {len(links_to_scrape)} links")
            self._scrape_links(links_to_scrape)
        except Exception as e:
            logging.error(f"An error occurred during scraping: {e}")
        finally:
            if self.driver:
                self.driver.quit()
        logging.info(f"Total documents collected: {len(self.documents)}")
        return self.documents

    def _scrape_links(self, links_to_scrape: List[str]) -> None:
        logging.info(f"Scraping links: {links_to_scrape}")
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = {
                executor.submit(self.scrape_page, url): url for url in links_to_scrape
            }
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    document = future.result()
                    if self._is_valid_document(document):
                        self.documents.append(document)
                except Exception as e:
                    logging.error(f"Error scraping {url}: {e}")

    def scrape_page(self, url: str) -> str:
        logging.info(f"Scraping page: {url}")
        if (
            not self.link_collector._is_same_domain_and_path(url)
            or url in self.visited_urls
        ):
            logging.info(f"Skipping URL (same domain or already visited): {url}")
            return ""
        self.visited_urls.add(url)
        if not self.robots_checker.is_allowed(urlparse(url).path):
            logging.info(f"Access to {url} disallowed by robots.txt.")
            return ""
        self.link_collector._wait_for_next_request()
        try:
            logging.info(f"Fetching URL: {url}")
            self.driver.set_page_load_timeout(self.config.page_load_timeout)
            self.driver.get(url)
            time.sleep(self.config.page_load_sleep)
            page_source = self.driver.page_source
            readable_text = extract_readable_text(page_source)
            logging.info(
                f"Readable Text: {readable_text[:50]}... Length: {len(readable_text)}"
            )
            return readable_text
        except TimeoutException:
            logging.error(f"Timeout while trying to load {url}")
        except WebDriverException as e:
            logging.error(f"WebDriver error: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
        return ""

    def _is_valid_document(self, document: str) -> bool:
        """
        Checks if the document meets the criteria for being considered a valid document.

        Args:
            document (str): The document text to be checked.

        Returns:
            bool: True if the document is valid, False otherwise.
        """
        return bool(document and len(document) > 100)
