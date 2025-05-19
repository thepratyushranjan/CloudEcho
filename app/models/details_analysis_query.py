# -*- coding: utf-8 -*-

from pydantic import BaseModel
from typing import Any, Dict

class DetailsAnalysisRequest(BaseModel):
    query: str
    request: Dict[str, Any]
    monitoring: Dict[str, Any]
