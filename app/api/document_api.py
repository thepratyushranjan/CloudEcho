# This file contains the API endpoints for the document service.

from fastapi import APIRouter, HTTPException
from app.models.document_query import DocumentRequest
from app.services.document_service import DocumentService

router = APIRouter()

@router.post("/document")
async def scrape_and_store_document(request: DocumentRequest):
    """
    Scrapes the webpage from the given URL, generates embeddings for the text chunks,
    and stores them in the database under the specified collection.
    """
    document_service = DocumentService()
    
    try:
        # Pass both the URL and the collection_name to the service
        result = document_service.scrape_and_store(request.url, request.collection_name, request.source_identifier)
        return {
            "url": request.url,
            "collection_name": request.collection_name,
            "message": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
