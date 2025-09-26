from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse

from .node_bridge import (
    NodeBridgeError,
    run_chat_helper,
    run_mcp_status_helper,
    stream_chat_helper,
)
from .schemas import ChatRequest, ChatResponse, MCPStatusResponse


def create_app() -> FastAPI:
    app = FastAPI(title="Agentic Chatbot Backend", version="0.1.0")

    @app.post("/chatbot/chat", response_model=ChatResponse)
    async def chat_endpoint(
        request: ChatRequest, stream: bool | None = Query(default=None)
    ) -> ChatResponse | StreamingResponse:
        query_stream = bool(request.stream)
        if stream is not None:
            query_stream = query_stream or stream

        payload = {
            "query": request.query,
            "messages": [message.model_dump() for message in request.messages],
            "stream": query_stream,
        }

        if query_stream:
            try:
                stream_gen = await stream_chat_helper(payload)
            except NodeBridgeError as exc:
                raise HTTPException(status_code=502, detail=str(exc)) from exc

            return StreamingResponse(
                stream_gen,
                media_type="application/x-ndjson; charset=utf-8",
                headers={
                    "Cache-Control": "no-cache, no-transform",
                    "Connection": "keep-alive",
                },
            )

        try:
            result = await run_chat_helper(payload)
        except NodeBridgeError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

        try:
            return ChatResponse(**result)
        except TypeError as exc:
            raise HTTPException(status_code=500, detail="Malformed response from agentic chatbot") from exc

    @app.get("/chatbot/mcp-status", response_model=MCPStatusResponse)
    async def mcp_status_endpoint() -> MCPStatusResponse:
        try:
            result = await run_mcp_status_helper({})
        except NodeBridgeError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

        return MCPStatusResponse(**result)

    return app


app = create_app()
