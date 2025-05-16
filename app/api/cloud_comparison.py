# -*- coding: utf-8 -*-

from fastapi import APIRouter, HTTPException
from services.cloud_comparison_service import CloudComparisonService
from models.cloud_comparison_query_model import CloudComparisonQueryRequest

router = APIRouter()

@router.post("/cloud-comparison")
async def cloud_comparison(request: CloudComparisonQueryRequest):
    """
    This API endpoint queries cloud instances based on location, vCPUs, and RAM.
    It returns cloud instances that match the given criteria.
    """
    cloud_comparison_service = CloudComparisonService()
    
    try:
        filtered_results = cloud_comparison_service.get_filtered_cloud_comparisons(
            location   = request.location,
            vcpus_min   = request.vcpus_min,
            vcpus_max   = request.vcpus_max,
            ram_gib_min = request.ram_gib_min,
            ram_gib_max = request.ram_gib_max,
        )
        
        return {"cloud_comparisons": filtered_results}
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"An error occurred: {str(e)}")
