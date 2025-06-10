# -*- coding: utf-8 -*-

from pydantic import BaseModel, field_validator, HttpUrl
from typing import Any, Dict, List, Optional, Union, Literal
from orm.cloud_response import CloudResponse


# This code defines a Pydantic model for a document request.
class DocumentRequest(BaseModel):
    url: Union[HttpUrl, str]
    collection_name: str
    source_identifier: str

    @classmethod
    def validate_url(cls, value):
        if value == "":
            return value
        return HttpUrl.validate(value)


# This code defines a Pydantic model for a query request.
class QueryRequest(BaseModel):
    query: str
    collection_name: str
    filter_dict: dict


# This code defines a Pydantic model for a simple query request.
class SimpleQueryRequest(BaseModel):
    query: str
    collection_name: Literal['Info'] = 'Info'
    

# This code defines a Pydantic model for a checklist analysis request.
class ChecklistAnalysisRequest(BaseModel):
    query: str
    request: Dict[str, Any]


# This code defines a Pydantic model for a details analysis request.
class DetailsAnalysisRequest(BaseModel):
    query: str
    request: Dict[str, Any]
    monitoring: Dict[str, Any]


# This code defines a Pydantic model for a cloud comparison query request.
class CloudComparisonQueryRequest(BaseModel):
    location: Optional[List[str]] = None
    vcpus_min: Optional[int]       = None
    vcpus_max: Optional[int]       = None
    ram_gib_min: Optional[float]   = None
    ram_gib_max: Optional[float]   = None

    @field_validator("location", mode="before")
    @classmethod
    def ensure_list(cls, v: Any):
        # allow single string or list
        if v is None:
            return v
        return [v] if isinstance(v, str) else v


# This code defines a Pydantic model for a cloud comparison query with multiple parameters.
class CloudComparisonQueryMultipleRequest(BaseModel):
    location: Optional[List[str]] = None
    clouds: Optional[List[str]] = None
    instance_families: Optional[List[str]] = None
    regions: Optional[List[str]] = None
    instance_type: Optional[List[str]] = None


# This code defines a Pydantic model for a cloud comparison filter request.
class CloudComparisonFilterRequest(BaseModel):
    """
    Filter criteria for cloud‐instance specs.
    Numeric fields will be used as upper bounds (<=).
    """
    vcpus: Optional[List[int]]               = None
    ram_gib: Optional[List[float]]           = None
    memory_mib: Optional[List[int]]          = None
    cost_per_hour: Optional[List[float]]     = None
    instance_families: Optional[List[str]] = None
    country: Optional[List[str]] = None
class CloudMultipleDataResponse(BaseModel):
    cloud_multiple_data: List[CloudResponse]


# This code defines a Pydantic model for a recommendation request(Cloud Tuner).
class RecommendationRequest(BaseModel):
    org_id:    str
    api_token: str
    limit:     int  = 3
    overview:  bool = True

# This code defines a Pydantic model for a resource request(Cloud Tuner).
class ResourceRequest(BaseModel):
    resource_id: str
    api_token:   str
    details:     bool = True

