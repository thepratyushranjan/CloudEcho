# -*- coding: utf-8 -*-

from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str
    collection_name: str
    filter_dict: dict
    