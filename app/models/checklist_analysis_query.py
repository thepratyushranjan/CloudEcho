# -*- coding: utf-8 -*-

from pydantic import BaseModel
from typing import Any, Dict

class ChecklistAnalysisRequest(BaseModel):
    query: str
    request: Dict[str, Any]
