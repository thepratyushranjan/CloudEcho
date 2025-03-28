# Pydantic model for query
from pydantic import BaseModel

DEFAULT_COLLECTION_NAME = "Data Source Connection"

class QueryRequest(BaseModel):
    query: str
    collection_name: str = DEFAULT_COLLECTION_NAME
