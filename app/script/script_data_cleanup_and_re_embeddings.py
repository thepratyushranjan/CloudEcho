import uuid
import re
from sqlalchemy import create_engine, Column, String, ForeignKey, JSON
from config.config import Config
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import sessionmaker, declarative_base
from pgvector.sqlalchemy import Vector
import google.generativeai as genai

Base = declarative_base()

class LanchainPgCollection(Base):
    __tablename__ = "langchain_pg_collection"
    uuid = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    cmetadata = Column(JSON, nullable=True)

class LangchainPgEmbedding(Base):
    __tablename__ = "langchain_pg_embedding"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    collection_id = Column(String, 
                           ForeignKey("langchain_pg_collection.uuid"), 
                           nullable=False)
    embedding = Column(Vector(), nullable=False)
    document = Column(String, nullable=False)
    cmetadata = Column(JSONB, nullable=True)

engine = create_engine(Config.POSTGRES_CONNECTION)
SessionLocal = sessionmaker(bind=engine)

GEMINI_API_KEY = Config.GEMINI_API_KEY

embedding_model = genai.GenerativeModel("models/embedding-001")
embedding_model_name = "models/embedding-001"

def mimic_case(match_str: str, replacement: str):
    if match_str.islower():
        return replacement.lower()
    if match_str.isupper():
        return replacement.upper()
    if match_str[0].isupper() and match_str[1:].islower():
        return replacement.capitalize()
    if match_str[0].islower() and any(c.isupper() for c in match_str[1:]):
        return "cloudTuner"
    result = []
    for i, char in enumerate(replacement):
        if i < len(match_str) and match_str[i].isupper():
            result.append(char.upper())
        else:
            result.append(char.lower())
    return "".join(result)

def clean_text(text: str):
    def replace_func(match: re.Match):
        found = match.group(0)
        return mimic_case(found, "cloudtuner")
    pattern = r"(?:optscale|hystax)"
    result = re.sub(pattern, replace_func, text, flags=re.IGNORECASE)
    return result.strip() if result else ""

def update_embeddings_in_db():
    session = SessionLocal()
    try:
        documents = session.query(LangchainPgEmbedding).all()
        print(f"Found {len(documents)} documents for processing.")

        for doc in documents:
            cleaned_text = clean_text(doc.document)
            if not cleaned_text:
                print(f"Document ID {doc.id} has empty cleaned text. Skipping.")
                continue

            doc.document = cleaned_text

            if doc.cmetadata is None:
                doc.cmetadata = {}

            doc.cmetadata["content"] = cleaned_text
            result = genai.embed_content(content=cleaned_text, model=embedding_model_name)
            new_embedding = result.get("embedding")
            if new_embedding is None:
                raise Exception(f"No embedding found in response for document ID {doc.id}")
            doc.embedding = new_embedding
            print(f"Updated document, cmetadata, and embedding for document ID: {doc.id}")
        session.commit()
        print("All embeddings updated successfully.")

    except Exception as e:
        session.rollback()
        print(f"Error during update: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    update_embeddings_in_db()
