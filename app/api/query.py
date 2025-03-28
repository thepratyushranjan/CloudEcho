
from fastapi import APIRouter, HTTPException
from app.models.query import QueryRequest
from app.services.query_service import QueryService

router = APIRouter()

@router.post("/query")
async def query_docs(request: QueryRequest):
    """
    Queries the documentation database using vector search.
    The endpoint receives a query (and optionally a collection_name),
    generates its embedding, performs a vector search, and returns the final answer.
    """
    query_service = QueryService()
    
    try:
        final_response = query_service.query_document(query=request.query, collection_name=request.collection_name)
        
        if not final_response:
            raise HTTPException(status_code=404, detail="No relevant documents found.")
        
        return {"response": final_response}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
