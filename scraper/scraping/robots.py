"""
Module to handle fetching and parsing robots.txt for web scraping permissions.
"""

import logging
from typing import Dict, List, Optional
from urllib.parse import urlparse

import requests

from scraper.config.logging import safe_run


class RobotsTxtChecker:
    """
    Fetches and parses the robots.txt file for a given website to manage scraping permissions.
    """

    def __init__(self, base_url: str, requester: Optional[requests.Session] = None):
        self.base_url = urlparse(base_url).netloc
        self.robots_url = f"http://{self.base_url}/robots.txt"
        self.requester = requester or requests.Session()
        self.rules: Dict[str, List[str]] = {}

    @safe_run
    def fetch(self) -> None:
        """Fetches and parses the robots.txt file."""
        try:
            response = self.requester.get(self.robots_url)
            response.raise_for_status()
            self._parse(response.text)
            logging.info("robots.txt fetched and parsed successfully.")
        except requests.RequestException as e:
            if e.response.status_code == 404:
                logging.warning(
                    f"robots.txt not found at {self.robots_url}, proceeding without it."
                )
            else:
                logging.error(f"Failed to fetch robots.txt from {self.robots_url}: {e}")
                raise ConnectionError(f"Error fetching robots.txt: {e}")

    @safe_run
    def is_allowed(self, path: str, user_agent: str = "*") -> bool:
        """Checks if the path is allowed by robots.txt for the given user agent."""
        if user_agent not in self.rules:
            return True
        for disallow_path in self.rules.get(user_agent, []):
            if path.startswith(disallow_path):
                logging.info(
                    f"Access to {path} disallowed for {user_agent} by robots.txt."
                )
                return False
        return True

    @safe_run
    def _parse(self, content: str) -> None:
        """Parses the robots.txt content."""
        current_user_agent = None
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("User-agent:"):
                current_user_agent = line.split(":")[1].strip()
                self.rules[current_user_agent] = []
            elif line.startswith("Disallow:") and current_user_agent is not None:
                disallow_path = line.split(":")[1].strip()
                self.rules[current_user_agent].append(disallow_path)
        logging.info("robots.txt rules parsed and stored.")
