"""
Module: dynamic_chunking.py
Purpose: Provides functionality for determining chunk sizes, chunking text data,
and converting data to JSON format.
"""

import json
import logging
from typing import List

from scraper.config.logging import safe_run


class DataChunker:
    """
    A class responsible for chunking text data and converting it to JSON format.
    """

    def __init__(self, chunk_factor: int = 20, min_chunk_size: int = 100):
        """
        Initializes the DataChunker with parameters for chunking.
        Args:
            chunk_factor (int): The factor to determine chunk size based on data length.
            min_chunk_size (int): The minimum size of each chunk.
        """
        self.chunk_factor = chunk_factor
        self.min_chunk_size = min_chunk_size

    def determine_chunk_size(self, data: str) -> int:
        """
        Determines the chunk size based on the length of the data.
        Args:
            data (str): The text data to be chunked.
        Returns:
            int: The determined chunk size.
        """
        return max(self.min_chunk_size, len(data) // self.chunk_factor)

    @safe_run
    def chunk_data(self, data: str) -> List[str]:
        """
        Splits the data into chunks based on the determined chunk size.
        Args:
            data (str): The text data to be chunked.
        Returns:
            List[str]: A list of text chunks.
        """
        size = self.determine_chunk_size(data)
        logging.info(f"Chunking data into size: {size}")
        return [data[i : i + size] for i in range(0, len(data), size)]

    @safe_run
    def data_to_json(self, data: List[str]) -> str:
        """
        Converts a list of data chunks into a JSON formatted string.
        Args:
            data (List[str]): A list of text chunks.
        Returns:
            str: A JSON formatted string representing the chunks.
        """
        try:
            json_data = json.dumps({"chunks": data})
            logging.info("Data successfully converted to JSON format.")
            return json_data
        except (TypeError, ValueError) as e:
            logging.error(f"Failed to convert data to JSON: {e}")
            raise
