"""
Custom errors for the scraper.
"""


class BaseError(Exception):
    """Base class for scraper exceptions."""

    pass


class BrowserLaunchError(BaseError):
    """Raised when the browser fails to launch."""

    pass


class PageScrapingError(BaseError):
    """Raised when the page scraping fails."""

    pass


class RobotsTxtError(BaseError):
    """Raised when there is an error with robots.txt handling."""

    pass


class QueryError(BaseError):
    """Raised when there is an error with LLM query."""

    pass
