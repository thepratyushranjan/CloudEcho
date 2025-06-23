from fastapi import APIRouter, HTTPException
from services.cloud_multiple_data_service import CloudMultipleDataService
from models.cloud_multiple_data_model import CloudComparisonQueryMultipleRequest, CloudMultipleDataResponse
import traceback

router = APIRouter()

@router.post("/cloud-comparison/cloud-provider", response_model=CloudMultipleDataResponse)
async def cloud_comparison_multiple(request: CloudComparisonQueryMultipleRequest):
    """
    This API endpoint queries cloud instances based on multiple location, clouds, instance families.
    It returns cloud instances that match the given criteria.
    """
    cloud_comparison_service = CloudMultipleDataService()
    
    try:
        filtered_results = cloud_comparison_service.get_filtered_cloud_comparisons_multiple(
            location=request.location, 
            clouds=request.clouds, 
            instance_families=request.instance_families,
            regions=request.regions,
            instance_type=request.instance_type
        )
        
        return CloudMultipleDataResponse(cloud_multiple_data=filtered_results)
    
    except HTTPException as e:
        raise e
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Unexpected error in cloud_comparison_multiple: {error_details}")
        raise HTTPException(status_code=400, detail=f"An error occurred: {str(e)}")
