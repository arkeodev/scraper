"""
Module to collect links from a given web page.
"""

import logging
import time
from typing import Callable, List
from urllib.parse import urljoin, urlparse, urlunparse

from selenium import webdriver

from scraper.config import AppConfig, ScraperConfig


class LinkCollector:
    """
    Collects all links from a base URL that are in the same domain and below the given URL path.
    """

    def __init__(self, base_url: str, driver: webdriver.Chrome, parser: Callable):
        """
        Initializes the LinkCollector with the base URL, WebDriver, and parser.

        Args:
            base_url (str): The base URL of the website to scrape.
            driver (webdriver.Chrome): The WebDriver instance for scraping.
            parser (Callable): The parser to use for extracting links (e.g., BeautifulSoup).
        """
        self.base_url = base_url
        self.base_path = urlparse(base_url).path
        self.driver = driver
        self.parser = parser
        self.visited_urls = set()
        self.last_request_time = 0

    def collect_all_links(
        self, page_load_timeout: int, page_load_sleep: int
    ) -> List[str]:
        """
        Collects all links under the base URL that are in the same domain and below the base URL path.

        Args:
            page_load_timeout (int): The timeout for loading pages.
            page_load_sleep (int): The sleep time after loading a page.

        Returns:
            List[str]: A list of collected links.
        """
        collected_links = []
        links_to_visit = [(self.base_url, 0)]  # Start with the base URL and depth 0.

        while links_to_visit and len(collected_links) < ScraperConfig().max_links:
            current_url, depth = links_to_visit.pop(
                0
            )  # Get the next URL to visit and its depth.
            if (
                current_url in self.visited_urls
                or depth > ScraperConfig().scraping_depth
            ):  # Skip if already visited or depth exceeds limit.
                continue

            self.visited_urls.add(current_url)  # Mark the URL as visited.

            new_links = self._get_links(
                current_url, page_load_timeout, page_load_sleep
            )  # Extract new links.
            for link in new_links:
                if (
                    link not in self.visited_urls
                    and len(collected_links) < ScraperConfig().max_links
                ):
                    links_to_visit.append(
                        (link, depth + 1)
                    )  # Add new links to visit list with incremented depth.
                    collected_links.append(link)  # Collect the new links.

        return collected_links

    def _get_links(
        self, url: str, page_load_timeout: int, page_load_sleep: int
    ) -> List[str]:
        """
        Extracts links from the given URL.

        Args:
            url (str): The URL to extract links from.
            page_load_timeout (int): The timeout for loading the page.
            page_load_sleep (int): The sleep time after loading the page.

        Returns:
            List[str]: A list of extracted links.
        """
        self._wait_for_next_request()  # Ensure minimum interval between requests.
        try:
            logging.info(f"Getting links from URL: {url}")
            self.driver.set_page_load_timeout(
                page_load_timeout
            )  # Set the page load timeout.
            self.driver.get(url)  # Load the URL.
            time.sleep(page_load_sleep)  # Wait for the specified sleep time.
            soup = self.parser(
                self.driver.page_source, "html.parser"
            )  # Parse the page source with BeautifulSoup.
            links = [
                urljoin(url, link["href"]) for link in soup.find_all("a", href=True)
            ]  # Extract all href links and join with the base URL.
            filtered_links = [
                self._normalize_link(link)
                for link in links
                if self._is_same_domain_and_path(link)
            ]  # Normalize and filter links to the same domain and path.
            filtered_links = list(set(filtered_links))  # Remove duplicate links.
            logging.info(
                f"Found {len(filtered_links)} same domain and path links from {url}"
            )
            return filtered_links
        except Exception as e:
            logging.error(f"Error while getting links from {url}: {e}")
            return []

    def _is_same_domain_and_path(self, url: str) -> bool:
        """
        Checks if the URL is in the same domain and path as the base URL.

        Args:
            url (str): The URL to check.

        Returns:
            bool: True if the URL is in the same domain and path, False otherwise.
        """
        parsed_url = urlparse(url)
        base_url_parsed = urlparse(self.base_url)
        return (
            parsed_url.netloc == base_url_parsed.netloc
            and parsed_url.path.startswith(self.base_path)
        )

    def _normalize_link(self, url: str) -> str:
        """
        Normalize URL by removing fragment identifiers and optionally query parameters.

        Args:
            url (str): The URL to normalize.

        Returns:
            str: The normalized URL.
        """
        parsed_url = urlparse(url)
        # Remove fragment identifiers and optionally query parameters.
        normalized_url = parsed_url._replace(fragment="", query="")
        return urlunparse(normalized_url)

    def _wait_for_next_request(self) -> None:
        """
        Ensures a minimum interval between requests to avoid overloading the server.
        """
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < AppConfig().min_interval_between_requests:
            wait_time = (
                AppConfig().min_interval_between_requests - time_since_last_request
            )
            logging.info(f"Waiting for {wait_time:.2f} seconds before next request")
            time.sleep(wait_time)
        self.last_request_time = time.time()  # Update the time of the last request.
