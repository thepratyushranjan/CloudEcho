from pydantic import BaseModel
from enum import Enum
from typing import Optional

class CloudEnum(str, Enum):
    AWS = 'AWS'
    Azure = 'Azure'
    GCP = 'GCP'

class CloudResponse(BaseModel):
    id: int
    region: str
    location: str
    instance_type: str
    instance_family: str
    vcpus: int
    ram_gib: float
    memory_mib: int
    cost_per_hour: Optional[float] = None
    cloud: CloudEnum
    class Config:
        from_attributes = True
