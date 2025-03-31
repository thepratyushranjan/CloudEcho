# -*- coding: utf-8 -*-

import psycopg2
from app.core.config import Config
from langchain_postgres.vectorstores import PGVector

class PGVectorStore:
    def __init__(self):
        self.connection = psycopg2.connect(Config.POSTGRES_CONNECTION)  # PostgreSQL connection
        self.vector_store = PGVector(connection=self.connection)  # PGVector store initialization

    def store_embeddings(self, chunks: list, embeddings: list):
        """
        Store the document chunks and their corresponding embeddings in PostgreSQL.
        """
        documents = [{"content": chunk, "embedding": embedding} for chunk, embedding in zip(chunks, embeddings)]
        self.vector_store.add_documents(documents)

    def query_embeddings(self, query_embedding):
        """
        Query the PostgreSQL database for the most relevant document chunks based on vector similarity.
        """
        return self.vector_store.similarity_search(query_embedding)
