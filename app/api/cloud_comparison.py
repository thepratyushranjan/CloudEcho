from fastapi import APIRouter, HTTPException
from services.cloud_comparison_service import CloudComparisonService
from models.cloud_comparison_query_model import CloudComparisonQueryRequest

router = APIRouter()

@router.post("/cloud-comparison")
async def cloud_comparison(request: CloudComparisonQueryRequest):
    """
    This API endpoint queries cloud instances based on region, vCPUs, and RAM.
    It returns cloud instances that match the given criteria.
    """
    cloud_comparison_service = CloudComparisonService()
    
    try:
        filtered_results = cloud_comparison_service.get_filtered_cloud_comparisons(
            region=request.region, 
            vcpus=request.vcpus, 
            ram_gib=request.ram_gib
        )
        
        # Return the filtered results
        return {"cloud_comparisons": filtered_results}
    
    except HTTPException as e:
        raise e  # Re-raise any exceptions for the API
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"An error occurred: {str(e)}")
