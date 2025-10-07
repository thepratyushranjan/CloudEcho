# models.py

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Text, String, JSON, ForeignKey, Float, Enum
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

Base = declarative_base()

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536))


class LanchainPgCollection(Base):
    __tablename__ = "langchain_pg_collection"
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    cmetadata = Column(JSON, nullable=True)

class LangchainPgEmbedding(Base):
    __tablename__ = "langchain_pg_embedding"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    collection_id = Column(UUID(as_uuid=True), 
                           ForeignKey("langchain_pg_collection.uuid"), 
                           nullable=False)
    embedding = Column(Vector(), nullable=False)
    document = Column(String, nullable=False)
    cmetadata = Column(JSONB, nullable=True)

class CloudComparison(Base):
    __tablename__ = "cloud_comparison"

    id = Column(Integer, primary_key=True, autoincrement=True)
    region = Column(String, nullable=False)
    location = Column(String, nullable=False)
    instance_type = Column(String, nullable=False)
    instance_family = Column(String, nullable=False)
    vcpus = Column(Integer, nullable=False)
    memory_gb = Column(String, nullable=False)
    os = Column(String, nullable=True)
    cost_per_hour = Column(Float, nullable=True)
    storage = Column(String, nullable=True)
    gpu = Column(String, nullable=True)
    virtualization_type = Column(String, nullable=True)
    term_type = Column(String, nullable=True)
    cpu_architecture = Column(String, nullable=True)
    vgeneration = Column(String, nullable=True)
    cloud = Column(
        Enum('AWS', 'Azure', 'GCP', name='cloud_enum'),
        nullable=False
    )