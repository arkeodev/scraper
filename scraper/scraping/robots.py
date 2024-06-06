from typing import Optional
from urllib.parse import urlparse

import requests
from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout


class RobotsTxtChecker:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.content = None

    def fetch(self) -> None:
        try:
            robots_url = f"{self.base_url.rstrip('/')}/robots.txt"
            response = requests.get(robots_url)

            if response.status_code == 404:
                self.content = "robots.txt not found. Proceeding with scraping."
                return

            response.raise_for_status()
            self.content = response.text

        except (HTTPError, ConnectionError, Timeout, RequestException) as e:
            raise ValueError(f"Error occurred while checking robots.txt: {e}")

    def is_allowed(self, user_agent: str = "*") -> bool:
        if self.content is None:
            raise ValueError("robots.txt content is not fetched yet.")

        if self.content == "robots.txt not found. Proceeding with scraping.":
            return True

        user_agent_directives = {}
        current_user_agent = None

        for line in self.content.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if line.lower().startswith("user-agent:"):
                current_user_agent = line.split(":")[1].strip()
                user_agent_directives[current_user_agent] = []
            elif line.lower().startswith("disallow:") and current_user_agent:
                path = line.split(":")[1].strip()
                user_agent_directives[current_user_agent].append(path)

        parsed_url = urlparse(self.base_url)
        path = parsed_url.path or "/"
        allowed = True

        for ua, disallowed_paths in user_agent_directives.items():
            if ua == "*" or ua.lower() in user_agent.lower():
                for disallowed_path in disallowed_paths:
                    if path.startswith(disallowed_path):
                        allowed = False
                        break

        return allowed
