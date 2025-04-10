import json
from sqlalchemy import Column, Integer, Text, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pgvector.sqlalchemy import Vector
import google.generativeai as genai



Base = declarative_base()

class FAQChunk(Base):
    __tablename__ = "faq"
    id = Column(Integer, primary_key=True, autoincrement=True)
    query = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    embedding = Column(Vector(), nullable=False)

DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/app"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

api_key = "AIzaSyAker6F4E8-U6drPx76tC8gFHv1dU9I2Ww"
genai.configure(api_key=api_key)

def get_embedding_for_query(query_text: str) -> list:
    embedding_response = genai.embed_content(
        content=query_text,
        model="models/embedding-001",
        task_type="retrieval_query",
    )
    return embedding_response["embedding"]

# Define or load your JSON data
raw_json = """
[
  {
    "query": "When to Choose Kubernetes on AWS vs. GCP vs. Azure for Real-Time Applications?",
    "answer": "Real-time applications require low latency, rapid scalability, and tight service integration. On AWS, EKS is ideal for ecosystems built on AWS with extensive native services. GCP's GKE is known for its straightforward setup and excellent scalability, particularly when integrated with advanced data analytics services. Azure’s AKS is optimal for organizations embedded in the Microsoft ecosystem, providing seamless integration with Azure AD and related tools. Refer to the respective E2E guides for Kubernetes, AWS, Azure, and GCP for specific trade-offs and optimizations."
  }
]

"""

data = json.loads(raw_json)
session = SessionLocal()

try:
    for item in data:
        query_text = item["query"]
        answer_text = item["answer"]
        embedding_vector = get_embedding_for_query(query_text)
        faq_entry = FAQChunk(
            query=query_text,
            answer=answer_text,
            embedding=embedding_vector
        )
        session.add(faq_entry)
    session.commit()
    print("Records inserted successfully.")

except Exception as e:
    session.rollback()
    print("An error occurred:", e)

finally:
    session.close()
