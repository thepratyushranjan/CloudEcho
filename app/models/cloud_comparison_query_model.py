from pydantic import BaseModel, field_validator
from typing import List, Optional, Any

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