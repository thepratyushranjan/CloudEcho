import google.generativeai as genai
from app.core.config import Config

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





# import google.generativeai as genai
# from app.core.config import Config

# class EmbeddingGenerator:
#     def __init__(self, embedding_model_name="models/embedding-001"):
#         """Initializes the EmbeddingGenerator with a Gemini embedding model."""
#         self.embedding_model_name = embedding_model_name
#         genai.configure(api_key=Config.GEMINI_API_KEY)
#         self.embedding_model = genai.GenerativeModel(self.embedding_model_name)

#     def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
#         """Generates embeddings for a list of texts using the Gemini API."""
#         try:
#             embeddings = []
#             for text in texts:
#                 response = genai.embed_content(
#                     model=self.embedding_model_name,
#                     content=text,
#                     task_type="retrieval_document",
#                     title=text[:50]
#                 )
#                 embeddings.append(response['embedding'])
#             return embeddings
#         except Exception as e:
#             raise Exception(f"Error generating embeddings for texts: {e}")
        
#     def embed_documents(self, texts: list[str]) -> list[list[float]]:
#         """Wraps generate_embeddings for producing embeddings for a list of documents."""
#         return self.generate_embeddings(texts)
    
    
# import google.generativeai as genai
# from app.core.config import Config # Assuming this holds GEMINI_API_KEY
# from langchain_core.embeddings import Embeddings # Import the base class
# from typing import List
# import traceback

# # Ensure the class inherits from LangChain's Embeddings
# class EmbeddingGenerator(Embeddings):
#     # Default dimension for embedding-001, adjust if using a different model
#     embedding_dim: int = 768

#     def __init__(self, embedding_model_name="models/embedding-001"):
#         """Initializes the EmbeddingGenerator with a Gemini embedding model."""
#         self.embedding_model_name = embedding_model_name
#         try:
#             # Configure API Key (this is idempotent, safe to call)
#             genai.configure(api_key=Config.GEMINI_API_KEY)
#             print("EmbeddingGenerator: Google GenAI configured.")
#             # No need to instantiate genai.GenerativeModel for embed_content
#         except Exception as e:
#             print(f"EmbeddingGenerator: Error configuring Google GenAI: {e}")
#             raise

#     # Method required by LangChain Embeddings interface
#     def embed_documents(self, texts: List[str]) -> List[List[float]]:
#         """Generates embeddings for a list of documents."""
#         print(f"EmbeddingGenerator: Embedding {len(texts)} documents...")
#         embeddings = []
#         for text in texts:
#             if not text: # Handle empty strings gracefully
#                 print("Warning: Embedding empty document string. Returning zero vector.")
#                 embeddings.append([0.0] * self.embedding_dim)
#                 continue
#             try:
#                 response = genai.embed_content(
#                     model=self.embedding_model_name,
#                     content=text,
#                     task_type="retrieval_document" # Use 'retrieval_document' for storing
#                     # Removed optional 'title' - often not needed
#                 )
#                 # --- FIX: Access dict key directly ---
#                 if isinstance(response, dict) and 'embedding' in response:
#                     embeddings.append(list(map(float, response['embedding'])))
#                 else:
#                     print(f"ERROR: Unexpected document embedding response format: {response}")
#                     embeddings.append([0.0] * self.embedding_dim) # Add fallback zero vector
#                 # -------------------------------------
#             except Exception as e:
#                 print(f"ERROR embedding document (first 50 chars): '{text[:50]}...'. Error: {e}")
#                 embeddings.append([0.0] * self.embedding_dim) # Add fallback zero vector
#         print(f"EmbeddingGenerator: Finished embedding documents.")
#         return embeddings

#     # Method required by LangChain Embeddings interface
#     def embed_query(self, query: str) -> List[float]:
#         """Generates an embedding for a single query."""
#         print(f"EmbeddingGenerator: Embedding query (first 50 chars): '{query[:50]}...'")
#         if not query: # Handle empty strings gracefully
#             print("Warning: Embedding empty query string. Returning zero vector.")
#             return [0.0] * self.embedding_dim
#         try:
#             response = genai.embed_content(
#                 model=self.embedding_model_name,
#                 content=query,
#                 task_type="retrieval_query" # <-- FIX: Use 'retrieval_query' for searching
#                 # Removed optional 'title'
#             )
#             # --- FIX: Access dict key directly ---
#             if isinstance(response, dict) and 'embedding' in response:
#                  result = list(map(float, response['embedding']))
#                  print(f"EmbeddingGenerator: Query embedding successful (vector length: {len(result)}).")
#                  return result
#             else:
#                 print(f"ERROR: Unexpected query embedding response format: {response}")
#                 # Raise the kind of error PGVector expects
#                 raise ValueError(f"Unexpected format from embedding API: {response}")
#             # -------------------------------------
#         except Exception as e:
#             print(f"CRITICAL: Error caught within embed_query for text '{query[:50]}...': {e}")
#             traceback.print_exc()
#              # Raise the specific error PGVector surface
#             raise ValueError(f"Error generating embedding for query: {e}") from e


