# models.py

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Text, String, JSON, ForeignKey, BigInteger, Float
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

class AWSInstanceType(Base):
    __tablename__ = "aws_instance_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    region = Column(String, nullable=False)
    instance_type = Column(String, nullable=False, unique=True)
    vcpus = Column(Integer, nullable=False)
    memory_mib = Column(BigInteger, nullable=False)
    ram_gib = Column(Float, nullable=False)
    network_performance = Column(String, nullable=False)
    storage_info = Column(JSON, nullable=True)
    accelerators = Column(JSON, nullable=True)

