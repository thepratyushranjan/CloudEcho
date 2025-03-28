# Pydantic model for document_query

from pydantic import BaseModel, HttpUrl

class DocumentRequest(BaseModel):
    url: HttpUrl
    collection_name: str
    source_identifier: str
