# app.py
import logging
import os
from typing import List

import requests
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

from scraper.config.config import QAConfig, ScraperConfig
from scraper.rag.qa import QuestionAnswering
from scraper.scraping.scraper import WebScraper

load_dotenv()

HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")


class ScraperApp:
    def __init__(self, config: ScraperConfig):
        self.config = config
        self.embedding_model = SentenceTransformer(
            "sentence-transformers/msmarco-distilbert-base-tas-b"
        )

    def scrape_and_process(self, url: str):
        if not self.is_valid_url(url):
            raise ValueError("Invalid URL format")
        if not self.url_exists(url):
            raise ValueError("The URL does not exist")

        scraper = WebScraper(url, config=self.config)
        documents = scraper.scrape()
        qa_instance = QuestionAnswering(documents)
        qa_instance.create_index()
        return qa_instance

    def is_valid_url(self, url: str) -> bool:
        from urllib.parse import urlparse

        parsed = urlparse(url)
        return bool(parsed.scheme) and bool(parsed.netloc)

    def url_exists(self, url: str) -> bool:
        try:
            response = requests.head(url, allow_redirects=True, timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
