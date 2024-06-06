# scraping/database/vector_db.py
import os

import faiss
import numpy as np
import streamlit as st
import torch
from transformers import AutoModel, AutoTokenizer


class VectorDatabase:
    def __init__(
        self,
        embedding_model_name="sentence-transformers/all-MiniLM-L6-v2",
        vector_db="FAISS",
    ):
        self.embedding_model_name = embedding_model_name
        self.vector_db = vector_db
        self.vector_store = None
        self.model, self.tokenizer = self._initialize_embeddings()

    def _initialize_embeddings(self):
        try:
            tokenizer = AutoTokenizer.from_pretrained(self.embedding_model_name)
            st.write(f"Loaded tokenizer for {self.embedding_model_name}")

            # Allocate device
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            model = AutoModel.from_pretrained(self.embedding_model_name).to(device)
            st.write(f"Loaded model on {device}")

            return model, tokenizer
        except Exception as e:
            st.error(f"Error loading model: {e}")
            raise e

    def embed_text(self, text):
        inputs = self.tokenizer(
            text, return_tensors="pt", padding=True, truncation=True
        )
        with torch.no_grad():
            outputs = self.model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1)
        return embeddings.numpy()

    def create_vector_store(self, documents):
        embeddings = [self.embed_text(doc["text"]) for doc in documents]
        embeddings = np.vstack(embeddings)
        self.vector_store = faiss.IndexFlatL2(embeddings.shape[1])
        self.vector_store.add(embeddings)

    def insert_documents(self, documents):
        embeddings = [self.embed_text(doc["text"]) for doc in documents]
        embeddings = np.vstack(embeddings)
        if self.vector_store:
            self.vector_store.add(embeddings)
        else:
            self.create_vector_store(documents)

    def get_vector_store(self):
        return self.vector_store
