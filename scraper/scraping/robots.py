from urllib.parse import urlparse

import requests
from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout


class RobotsTxtChecker:
    def __init__(self, base_url: str) -> None:
        """
        Initializes the RobotsTxtChecker with the base URL.

        Args:
            base_url (str): The base URL of the website to check.
        """
        self.base_url = base_url
        self.content: str = None

    def fetch(self) -> None:
        """
        Fetches the robots.txt file from the base URL.

        Raises:
            ValueError: If an error occurs while fetching the robots.txt file.
        """
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
        """
        Checks if the scraping is allowed based on the robots.txt content.

        Args:
            user_agent (str, optional): The user agent to check against. Defaults to "*".

        Raises:
            ValueError: If the robots.txt content is not fetched yet.

        Returns:
            bool: True if scraping is allowed, False otherwise.
        """
        if self.content is None:
            raise ValueError("robots.txt content is not fetched yet.")

        if self.content == "robots.txt not found. Proceeding with scraping.":
            return True

        user_agent_directives = self._parse_robots_txt()

        parsed_url = urlparse(self.base_url)
        path = parsed_url.path or "/"

        return self._is_path_allowed(user_agent, path, user_agent_directives)

    def _parse_robots_txt(self) -> dict:
        """
        Parses the robots.txt content into directives for each user agent.

        Returns:
            dict: A dictionary with user agents as keys and lists of disallowed paths as values.
        """
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

        return user_agent_directives

    def _is_path_allowed(
        self, user_agent: str, path: str, user_agent_directives: dict
    ) -> bool:
        """
        Checks if the given path is allowed for the specified user agent based on the directives.

        Args:
            user_agent (str): The user agent to check against.
            path (str): The path to check.
            user_agent_directives (dict): The parsed robots.txt directives.

        Returns:
            bool: True if the path is allowed, False otherwise.
        """
        allowed = True

        for ua, disallowed_paths in user_agent_directives.items():
            if ua == "*" or ua.lower() in user_agent.lower():
                for disallowed_path in disallowed_paths:
                    if path.startswith(disallowed_path):
                        allowed = False
                        break
                if not allowed:
                    break

        return allowed
