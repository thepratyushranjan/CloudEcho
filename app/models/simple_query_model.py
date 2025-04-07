# -*- coding: utf-8 -*-

from pydantic import BaseModel
from typing import Literal

class SimpleQueryRequest(BaseModel):
    query: str
    collection_name: Literal['Info'] = 'Info'
