from app.utils.similarity_search import perform_similarity_search
from app.utils.embedding import EmbeddingGenerator

class QueryService:
    def query_document(self, query: str, collection_name: str, k: int = 4):
        try:
            query_generator = EmbeddingGenerator()
            query_embedding = query_generator.embed_query(query)  # Generate query embedding
            
            results = perform_similarity_search(collection_name, query_embedding, k)
            return results
        except Exception as e:
            raise Exception(f"Error in query_document: {e}")
