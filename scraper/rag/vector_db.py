from typing import Dict, List

import streamlit as st
from pymilvus import (
    Collection,
    CollectionSchema,
    DataType,
    FieldSchema,
    connections,
    utility,
)
from sentence_transformers import SentenceTransformer

from scraper.config.config import MilvusConfig


class VectorDatabase:
    def __init__(self, config: MilvusConfig) -> None:
        """
        Initializes the VectorDatabase with the given configuration.

        Args:
            config (MilvusConfig): Configuration for the Milvus database and embedding model.
        """
        self.config = config
        self.embeddings = None
        self.collection = None

    def connect_to_milvus(self) -> None:
        """
        Connects to the Milvus server using the configuration provided.
        """
        try:
            connections.connect("default", host=self.config.host, port=self.config.port)
            st.success("Connected to Milvus server.")
        except Exception as e:
            st.error(f"Failed to connect to Milvus server: {e}")
            raise e

    def load_embedding_model(self) -> None:
        """
        Loads the SentenceTransformer embedding model.
        """
        self.embeddings = SentenceTransformer(self.config.embedding_model_name)

    def create_or_load_collection(self) -> None:
        """
        Creates or loads the Milvus collection based on the provided configuration.
        """
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=384),
        ]
        schema = CollectionSchema(fields)

        try:
            if not utility.has_collection(self.config.collection_name):
                self.collection = Collection(
                    name=self.config.collection_name, schema=schema
                )
                st.success("Collection created successfully.")
            else:
                self.collection = Collection(name=self.config.collection_name)
                st.success("Collection loaded successfully.")
        except Exception as e:
            st.error(f"Failed to create or load collection: {e}")
            raise e

    def embed_text(self, text: str) -> List[float]:
        """
        Embeds a given text using SentenceTransformer embeddings.

        Args:
            text (str): The text to embed.

        Returns:
            List[float]: The embedding vector.
        """
        if not self.embeddings:
            self.load_embedding_model()
        return self.embeddings.encode(text)

    def create_vector_store(self, documents: List[Dict[str, str]]) -> None:
        """
        Creates a vector store from the provided documents.

        Args:
            documents (List[Dict[str, str]]): A list of documents with text content.
        """
        if not self.collection:
            self.create_or_load_collection()

        embeddings = [self.embed_text(doc["text"]) for doc in documents]
        entities = [embeddings]

        try:
            self.collection.insert(entities)
            index_params = {
                "index_type": "IVF_FLAT",
                "params": {"nlist": 128},
                "metric_type": "L2",
            }
            self.collection.create_index(
                field_name="embedding", index_params=index_params
            )
            self.collection.load()
            st.success("Index created and collection loaded successfully.")
        except Exception as e:
            st.error(f"Failed to insert data or create index: {e}")
            raise e

    def insert_documents(self, documents: List[Dict[str, str]]) -> None:
        """
        Inserts new documents into the existing vector store.

        Args:
            documents (List[Dict[str, str]]): A list of documents with text content.
        """
        if not self.collection:
            self.create_or_load_collection()

        embeddings = [self.embed_text(doc["text"]) for doc in documents]
        entities = [embeddings]

        try:
            self.collection.insert(entities)
            self.collection.load()
        except Exception as e:
            st.error(f"Failed to insert documents: {e}")
            raise e

    def get_vector_store(self) -> Collection:
        """
        Returns the vector store collection.

        Returns:
            Collection: The Milvus collection object.
        """
        return self.collection
