import json
from fastapi import APIRouter, HTTPException
from services.details_data_cleanup import transform_data
from models.checklist_analysis_query import ChecklistAnalysisRequest
from utils.checklist_llm import ChecklistLlmGenerator

router = APIRouter()

@router.post("/checklist-analysis")
async def checklist_analysis(payload: ChecklistAnalysisRequest):
  
    try:
        content = payload.request
        query = payload.query
        transform_content = transform_data(content)
        data = {
            "content": transform_content,
            "question": query
            }
        final_data = json.dumps(data, indent=2)
        checklist_llm_generator = ChecklistLlmGenerator()
        response = checklist_llm_generator.llm_query(final_data)
        return {
            "response": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")