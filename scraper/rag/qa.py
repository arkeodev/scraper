# qa.py
import logging
from typing import Dict, List

from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain.vectorstores import VectorStore
from sentence_transformers import SentenceTransformer, util

from scraper.config.config import QAConfig
from scraper.rag.prompt_template import get_prompt_template


class QuestionAnswering:
    """
    Handles the question-answering functionality using a vector database for retrieval and a language model for generating responses.
    """

    def __init__(
        self,
        vector_store: VectorStore,
        documents: List[Dict[str, str]],
        qa_config: QAConfig,
        embedding_model: SentenceTransformer = None,
    ):
        self.vector_store = vector_store
        self.documents = documents
        self.qa_config = qa_config if qa_config else QAConfig()
        self.embedding_model = (
            embedding_model
            if embedding_model
            else SentenceTransformer(self.qa_config.embedding_model_name)
        )
        self.top_n_chunks = self.qa_config.top_n_chunks

    def retrieve_similar_chunks(self, question: str, n: int) -> List[str]:
        """
        Retrieves the top n similar chunks from the vector store based on the question.

        Args:
            question (str): The question asked by the user.
            n (int): The number of similar chunks to retrieve.

        Returns:
            List[str]: A list of similar chunks.
        """
        logging.info("Here1")
        question_embedding = self.embedding_model.encode(question)
        logging.info(f"Embedded question: {question_embedding}")
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        results = self.vector_store.search(
            data=[question_embedding],
            anns_field="embedding",
            param=search_params,
            limit=n,
            expr=None,
        )
        similar_chunks = [
            result.entity.get("document")
            for result in results[0]
            if result.entity.get("document")
        ]
        logging.info(f"Retrieved similar chunks: {similar_chunks}")
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
        if not chunks:
            logging.error("No chunks provided for reranking.")
            return []

        # Remove any None or empty string values from chunks
        chunks = [chunk for chunk in chunks if chunk]
        if not chunks:
            logging.error("All chunks are None or empty after filtering.")
            return []

        logging.debug(f"Chunks after filtering: {chunks}")

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
        logging.info(f"Received question: {question}")
        similar_chunks = self.retrieve_similar_chunks(question, self.top_n_chunks)
        # if not similar_chunks:
        #     logging.error("No similar chunks found for the question.")
        #     return "No relevant information found."

        # reranked_chunks = self.rerank_chunks(question, similar_chunks)
        # if not reranked_chunks:
        #     logging.error("Failed to rerank chunks.")
        #     return "Failed to retrieve relevant information."

        prompt_template = get_prompt_template()
        # context = " ".join(reranked_chunks)
        context = ""
        prompt = prompt_template.format(context=context, question=question)

        logging.debug(f"Constructed prompt: {prompt}")

        qa_chain = load_qa_chain(
            prompt_template=PromptTemplate(template=prompt_template)
        )
        try:
            response = qa_chain.run({"context": context, "question": question})
        except Exception as e:
            logging.error(f"Error during QA chain run: {e}")
            return "An error occurred during the question-answering process."

        logging.info(f"Returned answer: {response}")
        return response
