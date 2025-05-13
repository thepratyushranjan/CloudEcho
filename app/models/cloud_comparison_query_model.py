from pydantic import BaseModel
from typing import Optional

class CloudComparisonQueryRequest(BaseModel):
    region: Optional[str] = None
    vcpus: Optional[int] = None 
    ram_gib: Optional[float] = None
