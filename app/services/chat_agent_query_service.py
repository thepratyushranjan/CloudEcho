# -*- coding: utf-8 -*-

from utils.similarity_search import perform_similarity_search
from utils.simple_similarity_search import perform_simple_similarity_search, perform_faq_similarity_search
from utils.llm import LlmGenerator

# QueryService provides methods to query documents based on a given query string.
class QueryService:
    def query_document(self, query: str, collection_name: str, filter_dict: dict = None, k: int = 4):
       
        try:
            combined_prompt = perform_similarity_search(collection_name, query, filter_dict=filter_dict, top_k=k)
            llm_generator = LlmGenerator()
            final_response = llm_generator.llm_query(combined_prompt)
            return final_response
        except Exception as e:
            raise Exception(f"Error in query_document: {e}")



# SimpleQueryService provides methods to perform simple queries on documents.
class SimpleQueryService:
    def simple_query_document(self, query: str, collection_name: str, k: int = 4):
        try:
            faq_result = perform_faq_similarity_search(collection_name, query, top_k=1)
            if faq_result:
                print("FAQ result found, returning it.")
                return faq_result
            merged_content = perform_simple_similarity_search(collection_name, query, top_k=k)
            llm_generator = LlmGenerator()
            final_response = llm_generator.llm_query(merged_content, query)
            return final_response
            
        except Exception as e:
            raise Exception(f"Error in query_document: {e}")