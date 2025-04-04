# -*- coding: utf-8 -*-

from utils.similarity_search import perform_similarity_search
from utils.llm import LlmGenerator


class QueryService:
    def query_document(self, query: str, collection_name: str, filter_dict: dict = None, k: int = 4):
       
        try:
            combined_prompt = perform_similarity_search(collection_name, query, filter_dict=filter_dict, top_k=k)
            llm_generator = LlmGenerator()
            final_response = llm_generator.llm_query(combined_prompt)
            return final_response
        except Exception as e:
            raise Exception(f"Error in query_document: {e}")

