"""
Purpose: Generates metadata for documents.
"""

from datetime import datetime
from typing import Dict


def generate_metadata(document: str, url: str) -> Dict[str, str]:
    """
    Generates metadata for each document.

    Args:
        document (str): The document content.
        url (str): The URL from which the document was scraped.

    Returns:
        Dict[str, str]: The metadata dictionary.
    """
    return {
        "url": url,
        "length": str(len(document)),
        "timestamp": datetime.now().isoformat(),
    }
