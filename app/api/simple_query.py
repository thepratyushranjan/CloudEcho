# -*- coding: utf-8 -*-

from fastapi import APIRouter, HTTPException
from models.simple_query_model import SimpleQueryRequest
from services.simple_query_service import SimpleQueryService

router = APIRouter()

@router.post("/simple-query")
async def query_docs(request: SimpleQueryRequest):
    """
    Queries the documentation database using vector search.
    The endpoint receives a query (and optionally a collection_name),
    generates its embedding, performs a vector search, and returns the final answer.
    """
    simple_query_service = SimpleQueryService()
    
    try:
        final_response = simple_query_service.simple_query_document(
            query=request.query, 
            collection_name=request.collection_name, 
            )
        
        if not final_response:
            raise HTTPException(status_code=404, detail="No relevant documents found.")
        
        return {"response": final_response}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
