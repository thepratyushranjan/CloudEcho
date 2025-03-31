# -*- coding: utf-8 -*-

from app.core.config import Config
from app.utils.embedding import EmbeddingGenerator
from langchain_postgres.vectorstores import PGVector
import json

connection_string = Config.POSTGRES_CONNECTION
embedding_function = EmbeddingGenerator()

def perform_similarity_search(collection_name: str, query: str, filter_dict: dict, top_k: int = 4):
    vector_store = PGVector(
        embeddings=embedding_function,
        connection=connection_string,
        collection_name=collection_name,
        use_jsonb=True,
    )
    results = vector_store.similarity_search_with_relevance_scores(
        query,
        k=top_k,
        score_threshold=0.5,
        filter=filter_dict
    )
    merged_content = "\n\n".join([doc.page_content for doc, _ in results])
    prompt_data = {
        "content": merged_content,
        "question": query
    }
    combined_prompt = json.dumps(prompt_data, indent=2)
    return combined_prompt
