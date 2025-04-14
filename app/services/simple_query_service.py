# -*- coding: utf-8 -*-

from utils.simple_similarity_search import perform_simple_similarity_search, perform_faq_similarity_search
from utils.llm import LlmGenerator

class SimpleQueryService:
    def simple_query_document(self, query: str, collection_name: str, k: int = 4):
        try:
            faq_result = perform_faq_similarity_search(collection_name, query, top_k=1)
            if faq_result:
                return faq_result
            combined_prompt = perform_simple_similarity_search(collection_name, query, top_k=k)
            llm_generator = LlmGenerator()
            final_response = llm_generator.llm_query(combined_prompt)
            return final_response
            
        except Exception as e:
            raise Exception(f"Error in query_document: {e}")