# text_extractor.py
import logging

import trafilatura
from readability import Document


def extract_readable_text(html: str) -> str:
    """Extracts readable text from HTML content using readability-lxml."""
    try:
        doc = Document(html)
        readable_html = doc.summary()
        readable_text = trafilatura.extract(readable_html)
        return readable_text.strip()
    except Exception as e:
        logging.error(f"Error extracting text: {e}")
        return ""


def extract_text_trafilatura(html: str) -> str:
    """Extracts readable text from HTML content using trafilatura directly."""
    try:
        readable_text = trafilatura.extract(html)
        return readable_text.strip() if readable_text else ""
    except Exception as e:
        logging.error(f"Error extracting text with trafilatura: {e}")
        return ""
