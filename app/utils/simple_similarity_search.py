# -*- coding: utf-8 -*-

from config.config import Config
from utils.embedding import EmbeddingGenerator
from langchain_postgres.vectorstores import PGVector
import json

# Common configurations
connection_string = Config.POSTGRES_CONNECTION
embedding_function = EmbeddingGenerator()

def perform_faq_similarity_search(collection_name: str, query: str, top_k: int = 1):
    """
    Perform similarity search specifically for FAQ data.
    """
    vector_store = PGVector(
        embeddings=embedding_function,
        connection=connection_string,
        collection_name=collection_name,
        use_jsonb=True,
    )
    results = vector_store.similarity_search_with_relevance_scores(
        query,
        k=top_k,
        score_threshold=0.7,
        filter={"source": "faq"}
    )
    final_content = "\n\n".join([doc.page_content for doc, _ in results])
    return final_content

def perform_simple_similarity_search(collection_name: str, query: str, top_k: int = 4):
    """
    Perform a general similarity search and return a combined prompt.
    """
    vector_store = PGVector(
        embeddings=embedding_function,
        connection=connection_string,
        collection_name=collection_name,
        use_jsonb=True,
    )
    results = vector_store.similarity_search(
        query,
        k=top_k,
        score_threshold=0.9,
    )
    merged_content = "\n\n".join([doc.page_content for doc in results])
    # prompt_data = {
    #     "content": merged_content,
    #     "question": query
    # }
    # combined_prompt = json.dumps(prompt_data, indent=2)
    return merged_content
