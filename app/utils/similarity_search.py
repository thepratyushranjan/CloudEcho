from app.core.config import Config
from app.utils.embedding import EmbeddingGenerator
from langchain_postgres.vectorstores import PGVector

connection_string = Config.POSTGRES_CONNECTION
embedding_function = EmbeddingGenerator()

def perform_similarity_search(collection_name: str, query_embedding: list, k: int = 4):
    vector_store = PGVector(
        embeddings=embedding_function,
        connection=connection_string,
        collection_name=collection_name,
        use_jsonb=True,
    )
    print(f"\nPerforming similarity search in collection '{collection_name}'")
    
    response = vector_store.similarity_search_by_vector(query_embedding, k)
    return response
