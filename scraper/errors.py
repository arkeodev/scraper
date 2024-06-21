"""
Custom errors for the scraper.
"""


class ScraperError(Exception):
    """Base class for scraper exceptions."""

    pass


class BrowserLaunchError(ScraperError):
    """Raised when the browser fails to launch."""

    pass


class PageScrapingError(ScraperError):
    """Raised when the page scraping fails."""

    pass


class RobotsTxtError(ScraperError):
    """Raised when there is an error with robots.txt handling."""

    pass


class CreateIndexError(ScraperError):
    """Raised when there is an error with index creation."""

    pass


class QueryError(ScraperError):
    """Raised when there is an error with LLM query."""

    pass
