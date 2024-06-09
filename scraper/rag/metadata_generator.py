from datetime import datetime


def generate_metadata(document: str, url: str) -> dict:
    """Generates metadata for each document."""
    return {
        "url": url,
        "length": len(document),
        "timestamp": datetime.now().isoformat(),
    }
