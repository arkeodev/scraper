"""
Module: qa.py
Purpose: Handles the question-answering functionality, including retrieval, reranking,
and generating responses using a prompt template.
"""

import logging
from typing import Dict, List

from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain.vectorstores import VectorStore
from sentence_transformers import SentenceTransformer, util

from scraper.config.config import MilvusConfig, QAConfig
from scraper.rag.prompt_template import get_prompt_template


class QuestionAnswering:
    """
    Handles the question-answering functionality using a vector database for retrieval and a language model for generating responses.
    """

    def __init__(
        self,
        vector_store: VectorStore,
        documents: List[Dict[str, str]],
        config: MilvusConfig = None,
        embedding_model: SentenceTransformer = None,
    ):
        self.vector_store = vector_store
        self.documents = documents
        self.config = config if config else MilvusConfig()
        self.embedding_model = (
            embedding_model
            if embedding_model
            else SentenceTransformer(self.config.embedding_model_name)
        )
        self.top_n_chunks = QAConfig().top_n_chunks

    def retrieve_similar_chunks(self, question: str, n: int) -> List[str]:
        """
        Retrieves the top n similar chunks from the vector store based on the question.

        Args:
            question (str): The question asked by the user.
            n (int): The number of similar chunks to retrieve.

        Returns:
            List[str]: A list of similar chunks.
        """
        question_embedding = self.embedding_model.encode(question).tolist()
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        results = self.vector_store.search(
            data=[question_embedding],
            anns_field="embedding",
            param=search_params,
            limit=n,
            expr=None,
        )
        similar_chunks = [result.entity.get("document") for result in results[0]]
        return similar_chunks

    def rerank_chunks(self, question: str, chunks: List[str]) -> List[str]:
        """
        Reranks the retrieved chunks based on their relevance to the question.

        Args:
            question (str): The question asked by the user.
            chunks (List[str]): The retrieved chunks.

        Returns:
            List[str]: The reranked chunks.
        """
        question_embedding = self.embedding_model.encode(
            question, convert_to_tensor=True
        )
        chunk_embeddings = self.embedding_model.encode(chunks, convert_to_tensor=True)
        reranked_indices = self._calculate_similarities(
            question_embedding, chunk_embeddings
        )
        return [chunks[i] for i in reranked_indices]

    def _calculate_similarities(
        self, question_embedding, chunk_embeddings
    ) -> List[int]:
        """
        Calculates the similarities between the question embedding and chunk embeddings.

        Args:
            question_embedding: The embedding of the question.
            chunk_embeddings: The embeddings of the chunks.

        Returns:
            List[int]: The indices of the chunks sorted by similarity.
        """
        similarities = util.pytorch_cos_sim(question_embedding, chunk_embeddings)
        reranked_indices = similarities[0].argsort(descending=True).tolist()
        return reranked_indices

    def answer_question(self, question: str) -> str:
        """
        Generates an answer to the question using the retrieved and reranked chunks and a prompt template.

        Args:
            question (str): The question asked by the user.

        Returns:
            str: The generated answer.
        """
        similar_chunks = self.retrieve_similar_chunks(question, self.top_n_chunks)
        reranked_chunks = self.rerank_chunks(question, similar_chunks)

        prompt_template = get_prompt_template()
        context = " ".join(reranked_chunks)
        prompt = prompt_template.format(context=context, question=question)

        qa_chain = load_qa_chain(
            prompt_template=PromptTemplate(template=prompt_template)
        )
        response = qa_chain.run({"context": context, "question": question})
        return response
