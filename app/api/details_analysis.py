import json
from fastapi import APIRouter, HTTPException
from services.details_data_cleanup import (
    transform_data,
    structure_metrics,
    structured_data,
    )
from models.details_analysis_query import DetailsAnalysisRequest
from utils.details_llm import DetailsLlmGenerator

router = APIRouter()

@router.post("/details-analysis")
async def details_analysis(payload: DetailsAnalysisRequest):
  
    try:
        sources = payload.request
        query = payload.query
        monitoring = payload.monitoring
        transform_monitoring = structure_metrics(monitoring)
        transform_sources = transform_data(sources)
        content = structured_data(
            transform_sources, 
            transform_monitoring
            )
        data = {
            "content": content,
            "question": query
            }
        final_data = json.dumps(data, indent=2)
        details_llm_generator = DetailsLlmGenerator()
        response = details_llm_generator.llm_query(final_data)
        return {
            "response": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")