from fastapi import APIRouter, HTTPException, Request
import json
from services.details_data_cleanup import transform_data  # Updated import

router = APIRouter()

@router.post("/details-analysis")
async def details_analysis(request: Request):
    """
    Receives any JSON payload, transforms it via transform_data(),
    writes the transformed result to disk, and returns it.
    """
    try:
        parsed_request = await request.json()
        transformed = transform_data(parsed_request)  # Updated function call
        return transformed
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")