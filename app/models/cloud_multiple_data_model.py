from pydantic import BaseModel
from typing import Optional, List
from orm.cloud_response import CloudResponse

class CloudComparisonQueryMultipleRequest(BaseModel):
    location: Optional[List[str]] = None
    clouds: Optional[List[str]] = None
    instance_families: Optional[List[str]] = None

class CloudMultipleDataResponse(BaseModel):
    cloud_multiple_data: List[CloudResponse]
