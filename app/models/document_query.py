
# Pydantic model for document_query

from pydantic import BaseModel, HttpUrl
from typing import Union

class DocumentRequest(BaseModel):
    url: Union[HttpUrl, str]
    collection_name: str
    source_identifier: str

    @classmethod
    def validate_url(cls, value):
        if value == "":
            return value
        return HttpUrl.validate(value)