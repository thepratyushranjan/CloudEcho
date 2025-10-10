from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class ChatContext(BaseModel):
    organization_id: Optional[str] = None
    cloud_account_id: Optional[str] = None


class ChatRequest(BaseModel):
    query: str = Field(..., description="Latest user utterance")
    messages: list[ChatMessage] = Field(
        default_factory=list,
        description="Prior conversation history",
    )
    stream: bool | None = Field(
        default=None,
        description="Set to true (or use ?stream=1) to request newline-delimited streaming responses.",
    )
    context: Optional[ChatContext] = Field(
        default=None,
        description="Optional context for the chat request",
    )


class ChatResponse(BaseModel):
    result: str
    reasoning: str | None = None
    modelUsed: str | None = None


class MCPStatusResponse(BaseModel):
    connected: bool
    result: str | None = None
    error: str | None = None


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
    memory_gb: str
    os: str
    cost_per_hour: Optional[float] = None
    cloud: CloudEnum
    class Config:
        from_attributes = True


__all__ = [
    "ChatContext",
    "ChatMessage",
    "ChatRequest",
    "ChatResponse",
    "MCPStatusResponse",
]
