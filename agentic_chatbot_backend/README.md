
# FastAPI Backend for the Agentic Chatbot

This package contains a self-contained FastAPI application (Python + Node helpers) that serves the agentic chatbot APIs without depending on the Next.js runtime.

## Features

- `POST /chatbot/chat` → runs the full agentic workflow (tool planning/execution + AI response).
- `GET /chatbot/mcp-status` → reports the health of configured MCP providers.

## Project layout

```
fastapi_backend/
├── node_app/          # Reused agentic workflow (lib/, handlers/, prompt/…)
├── node_scripts/      # Entry points invoked from FastAPI (chat.mjs, mcp-status.mjs)
├── main.py            # FastAPI application factory
├── node_bridge.py     # Async bridge between Python and Node
├── config.py          # Paths + node executable lookup
├── schemas.py         # Pydantic models for request/response validation
├── mcp-config.json    # MCP provider definitions (override via MCP_CONFIG_PATH)
├── package.json       # Node dependencies (ai SDK + MCP SDK)
└── requirements.txt   # Python dependencies
```

## Running locally

```bash
pip install -r fastapi_backend/requirements.txt
npm install --prefix fastapi_backend
uvicorn fastapi_backend.main:app --reload
```

Run the commands from the repository root (or set `NODE_EXECUTABLE` / `MCP_CONFIG_PATH` as needed) so the Node helpers resolve correctly.

### Required environment variables

All variables required by the original Node workflow still apply (e.g. `GOOGLE_GENERATIVE_AI_API_KEY`, `GOOGLE_GEMINI_MODEL`, `GOOGLE_GEMINI_FLASH_MODEL`, MCP endpoints, thinking budgets, etc.).

Optional overrides:

- `NODE_EXECUTABLE` – custom path to the Node runtime if `node` is not on `PATH`.
- `MCP_CONFIG_PATH` – absolute path to an alternative MCP config JSON.

## Testing the endpoints

```bash
http POST :8000/chatbot/chat query="Show me the latest costs" messages:='[]'
http GET  :8000/chatbot/mcp-status
```

(`http` is from [httpie](https://httpie.io/); curl or any HTTP client works.)

## Notes

- Streaming mode (`stream=1`) is ignored for now; the helper still returns the full response body.
- Errors from the Node logic surface as HTTP 502 to make troubleshooting easier.
- Update the files under `node_app/` to change the chatbot behaviour for both routes.

## Docker

Build and run the standalone container from the repo root:

```bash
docker build -f fastapi_backend/Dockerfile -t agentic-fastapi .
docker run --rm -p 8000:8000 \
  -e GOOGLE_GENERATIVE_AI_API_KEY=... \
  -e GOOGLE_GEMINI_MODEL=gemini-2.5-pro \
  -e GOOGLE_GEMINI_FLASH_MODEL=gemini-2.5-flash \
  agentic-fastapi
```
