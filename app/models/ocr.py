# -*- coding: utf-8 -*-

from pydantic import BaseModel

class OcrRequest(BaseModel):
    """
    Request model for OCR processing.
    """
    base64_string: str