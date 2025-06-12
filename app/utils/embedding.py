# -*- coding: utf-8 -*-

import google.generativeai as genai
from config.config import Config

class EmbeddingGenerator:
    def __init__(self, embedding_model_name="models/embedding-001"):
        """Initializes the EmbeddingGenerator with a Gemini embedding model."""
        self.embedding_model_name = embedding_model_name
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.embedding_model = genai.GenerativeModel(self.embedding_model_name)

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generates embeddings for a list of texts using the Gemini API."""
        try:
            embeddings = []
            for text in texts:
                response = genai.embed_content(
                    model=self.embedding_model_name,
                    content=text,
                    task_type="retrieval_document",
                    title=text[:50]
                )
                embeddings.append(response['embedding'])
            return embeddings
        except Exception as e:
            raise Exception(f"Error generating embeddings for texts: {e}")
        
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Wraps generate_embeddings for producing embeddings for a list of documents."""
        return self.generate_embeddings(texts)

    def embed_query(self, query: str) -> list[float]:
        """Generates an embedding for a single query using the Gemini API."""
        try:
            response = genai.embed_content(
                model=self.embedding_model_name,
                content=query,
                task_type="retrieval_query"
            )
            return response['embedding']
        except Exception as e:
            raise Exception(f"Error generating embedding for query: {e}")


