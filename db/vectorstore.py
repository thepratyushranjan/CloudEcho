#PGVector integration for storing embeddings

import uuid
from app.core.config import Config
from langchain_postgres.vectorstores import PGVector
from app.utils.embedding import EmbeddingGenerator
from langchain.docstore.document import Document

class PGVectorStore:
    def __init__(self, collection_name: str):
        """
        Initializes the PGVectorStore class, connecting to PostgreSQL using the connection string in the Config class.
        Uses the provided collection_name to store the embeddings.
        """
        try:
            connection = Config.POSTGRES_CONNECTION
            embedding_generator = EmbeddingGenerator()
            self.vector_store = PGVector(
                embeddings=embedding_generator,
                connection=connection,
                collection_name=collection_name,
                use_jsonb=True
            )
        except Exception as e:
            raise Exception(f"Error connecting to PostgreSQL: {e}")

    # def store_embeddings(self, chunks: list, embeddings: list):
    #     """
    #     Stores document chunks and their corresponding embeddings in the PostgreSQL database.
    #     """
    #     try:
    #         documents = []
    #         expected_dimension = None

    #         for chunk, embedding in zip(chunks, embeddings):
    #             if expected_dimension is None:
    #                 expected_dimension = len(embedding)

    #             if len(embedding) != expected_dimension:
    #                 raise ValueError(
    #                     f"Inconsistent embedding dimension. Expected {expected_dimension}, got {len(embedding)} for chunk: {chunk[:50]}..."
    #                 )
    #             # Ensure embeddings are floats
    #             embedding = [float(x) for x in embedding]
    #             doc = Document(page_content=chunk, metadata={"content": chunk, "embedding": embedding})
    #             doc.id = str(uuid.uuid4())
    #             documents.append(doc)

    #         print(f"Number of documents to add: {len(documents)}")
    #         if documents:
    #             self.vector_store.add_documents(documents)
    #         else:
    #             print("No documents to add.")
    #     except Exception as e:
    #         raise Exception(f"Error storing embeddings in the database: {e}")

    def store_embeddings(self, chunks: list, embeddings: list, source_identifier: str):
        try:
            documents = []
            expected_dimension = None

            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                if expected_dimension is None:
                    expected_dimension = len(embedding)

                if len(embedding) != expected_dimension:
                    raise ValueError(
                        f"Warning: Skipping chunk {i} from '{source_identifier}' due to inconsistent embedding dimension. Expected {expected_dimension}, got {len(embedding)}."
                    )
                embedding = [float(x) for x in embedding]
                doc_metadata = {
                    "content": chunk,
                    "embedding": embedding,
                    "source": source_identifier,
                    "chunk_sequence": i
                }
                doc = Document(page_content=chunk, metadata=doc_metadata)
                doc.id = str(uuid.uuid4())
                documents.append(doc)

            print(f"Number of documents to attempt adding from '{source_identifier}': {len(documents)}")

            if documents:
                added_ids = self.vector_store.add_documents(documents)
                print(f"Successfully added {len(added_ids)} documents from '{source_identifier}'.")
            else:
                print(f"No documents to add from '{source_identifier}'.")
        except Exception as e:
            raise Exception(f"Error storing embeddings for source '{source_identifier}': {e}")



