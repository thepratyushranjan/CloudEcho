# This file contains the API endpoints for the document service.
import os
from fastapi import APIRouter, HTTPException
from models.document_query import DocumentRequest
from services.document_service import DocumentService

router = APIRouter()

json_filepath = os.path.abspath("tests/Q&N.json")
@router.post("/document")
async def scrape_and_store_document(request: DocumentRequest):
    """
    Scrapes the webpage from the given URL, generates embeddings for the text chunks,
    and stores them in the database under the specified collection.
    """
    document_service = DocumentService()
    
    try:
        # Pass both the URL and the collection_name to the service
        result = document_service.scrape_and_store(request.url, request.collection_name, request.source_identifier, json_filepath=json_filepath)
        return {
            "url": request.url,
            "collection_name": request.collection_name,
            "message": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
