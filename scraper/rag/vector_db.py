"""
Module: vector_db.py
Purpose: Manages interactions with a vector database (Milvus) for storing, indexing,
and retrieving embedded text data along with its metadata.
"""

import json
import logging
from typing import Dict, List

from pymilvus import (
    Collection,
    CollectionSchema,
    DataType,
    FieldSchema,
    connections,
    utility,
)
from pymilvus.exceptions import MilvusException
from sentence_transformers import SentenceTransformer

from scraper.config.config import MilvusConfig
from scraper.config.logging import safe_run
from scraper.rag.dynamic_chunking import DataChunker
from scraper.rag.metadata_generator import generate_metadata
from scraper.utility.utils import generate_collection_name


class VectorDatabase:
    """
    Manages vector database operations including collection management, document insertion,
    and embedding handling using Milvus.
    """

    def __init__(
        self,
        url: str,
        config: MilvusConfig = None,
        embedding_model: SentenceTransformer = None,
        chunker: DataChunker = None,
    ):
        """
        Initializes the VectorDatabase with configuration, an embedding model, and a data chunker.
        Args:
            url (str): Web URL be scraped.
            config (MilvusConfig): Configuration for the database connection and collection management.
            embedding_model (SentenceTransformer, optional): Preloaded embedding model for text vectorization.
            chunker (DataChunker, optional): An instance of DataChunker for chunking documents.
        """
        self.url = url
        self.config = config if config else MilvusConfig()
        self.embedding_model = (
            embedding_model
            if embedding_model
            else SentenceTransformer(self.config.embedding_model_name)
        )
        self.chunker = chunker if chunker else DataChunker()
        self.collection = None

    def connect_to_milvus(self) -> None:
        """
        Connects to the Milvus server using the configuration provided.
        """
        try:
            connections.connect("default", host=self.config.host, port=self.config.port)
            logging.info("Connected to Milvus server.")
        except MilvusException as e:
            logging.error(f"Failed to connect to Milvus server: {e}")
            raise e

    def get_collection_name(self) -> str:
        return generate_collection_name(self.url)

    @safe_run
    def create_or_load_collection(self, collection_name: str):
        """
        Creates or loads a collection in Milvus with the given name.
        Args:
            collection_name (str): The name of the collection to manage.
        """
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(
                name="embedding",
                dtype=DataType.FLOAT_VECTOR,
                dim=self.embedding_model.get_sentence_embedding_dimension(),
            ),
            FieldSchema(name="document", dtype=DataType.VARCHAR, max_length=4096),
            FieldSchema(
                name="metadata", dtype=DataType.VARCHAR, max_length=4096
            ),  # Assuming JSON data will be stored as string
        ]
        schema = CollectionSchema(
            fields,
            description="Collection for storing text documents with embeddings and metadata.",
        )

        # if utility.has_collection(collection_name):
        #     utility.drop_collection(collection_name)
        #     logging.info(f"Existing collection {collection_name} dropped.")

        self.collection = Collection(name=collection_name, schema=schema)
        logging.info(f"Collection {collection_name} created successfully.")

    @safe_run
    def create_vector_store(self):
        """
        Creates an index for the vector store.
        Args:
            collection_name (str): The name of the collection to create or load.
        """
        self.create_or_load_collection(self.get_collection_name())
        index_params = {
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128},
            "metric_type": "L2",
        }
        self.collection.create_index(field_name="embedding", index_params=index_params)
        self.collection.load()
        logging.info("Index created and collection loaded successfully.")

    @safe_run
    def insert_documents(self, documents: List[Dict[str, str]]):
        """
        Processes, embeds, and inserts documents into the vector database.
        Args:
            documents (List[Dict[str, str]]): List of document texts to process and store.
            collection_name (str): The name of the collection where documents will be inserted.
        """
        for document in documents:
            if not isinstance(document, dict) or "text" not in document:
                logging.error(f"Invalid document format: {document}")
                continue

            logging.info(f"Processing document: {document['text'][:50]}...")

            chunks = self.chunker.chunk_data([document["text"]])
            for chunk in chunks:
                if isinstance(chunk, list):
                    chunk = chunk[0]

                embedding = self.embedding_model.encode(chunk).tolist()
                metadata = generate_metadata(chunk, self.url)
                json_data = json.dumps({"text": chunk, "metadata": metadata})

                logging.debug(f"Embedding: {embedding[:5]}... Length: {len(embedding)}")
                logging.debug(f"Document: {chunk[:50]}...")
                logging.debug(f"Metadata: {metadata}")

                try:
                    self.collection.insert(
                        [
                            {
                                "embedding": embedding,
                                "document": chunk,
                                "metadata": json_data,
                            }
                        ]
                    )
                except Exception as e:
                    logging.error(
                        f"Failed to insert document chunk: {chunk[:50]}... Error: {e}"
                    )
        logging.info(f"Documents inserted successfully into database.")

    def get_vector_store(self) -> Collection:
        """
        Returns the vector store collection.
        Returns:
            Collection: The Milvus collection object.
        """
        return self.collection
