# -*- coding: utf-8 -*-

from pydantic import BaseModel

class ResourceRequest(BaseModel):
    resource_id: str
    api_token:   str
    details:     bool = True