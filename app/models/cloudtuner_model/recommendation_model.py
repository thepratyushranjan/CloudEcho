# -*- coding: utf-8 -*-

from pydantic import BaseModel

class RecommendationRequest(BaseModel):
    org_id:    str
    api_token: str
    limit:     int  = 3
    overview:  bool = True
