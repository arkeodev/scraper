"""
Purpose: Utility functions for the application.
"""

import hashlib


def generate_collection_name(url: str) -> str:
    """
    Generates a valid collection name by hashing the URL and prepending 'collection_'.

    Args:
        url (str): The URL to be hashed.

    Returns:
        str: The generated collection name.
    """
    hash_object = hashlib.md5(url.encode())
    return f"collection_{hash_object.hexdigest()}"
