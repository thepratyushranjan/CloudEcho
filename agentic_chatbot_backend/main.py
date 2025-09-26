from __future__ import annotations

from fastapi import FastAPI, HTTPException

from .node_bridge import NodeBridgeError, run_chat_helper, run_mcp_status_helper
from .schemas import ChatRequest, ChatResponse, MCPStatusResponse


def create_app() -> FastAPI:
    app = FastAPI(title="Agentic Chatbot Backend", version="0.1.0")

    @app.post("/chatbot/chat", response_model=ChatResponse)
    async def chat_endpoint(request: ChatRequest) -> ChatResponse:
        payload = {
            "query": request.query,
            "messages": [message.model_dump() for message in request.messages],
            "stream": bool(request.stream),
        }
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
