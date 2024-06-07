from langchain.chains import RetrievalQA
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Milvus
from sentence_transformers import SentenceTransformer
from transformers import pipeline


class QuestionAnswering:
    def __init__(
        self,
        collection,
        documents,
        embedding_model_name="sentence-transformers/all-MiniLM-L6-v2",
        qa_model_name="distilbert-base-uncased-distilled-squad",
    ):
        self.collection = collection
        self.documents = documents
        self.embedding_model_name = embedding_model_name
        self.qa_model_name = qa_model_name
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.qa_pipeline = pipeline("question-answering", model=qa_model_name)
        self.qa_chain = self._setup_retrieval_qa_chain()

    def _setup_retrieval_qa_chain(self):
        retriever = Milvus(self.collection, self.embedding_model)
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.qa_pipeline,
            chain_type="refine",
            retriever=retriever,
            return_source_documents=False,
        )
        return qa_chain

    def answer_question(self, question):
        result = self.qa_chain.run({"query": question})
        return result["result"]
