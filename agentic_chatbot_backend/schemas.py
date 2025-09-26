from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


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


class ChatResponse(BaseModel):
    result: str
    reasoning: str | None = None
    plannedTools: list[str] = Field(default_factory=list)
    toolCalls: list[Any] = Field(default_factory=list)
    toolResults: list[Any] = Field(default_factory=list)
    toolsExecuted: bool = False
    modelUsed: str | None = None


class MCPStatusResponse(BaseModel):
    ok: bool
    connected: bool
    result: str | None = None
    totalProviders: int = 0
    totalTools: int | None = None
    providers: dict[str, list[str]] | None = None
    error: str | None = None


__all__ = [
    "ChatMessage",
    "ChatRequest",
    "ChatResponse",
    "MCPStatusResponse",
]
