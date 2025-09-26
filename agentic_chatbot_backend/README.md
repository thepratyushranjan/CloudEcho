
# FastAPI Backend for the Agentic Chatbot

This package contains a self-contained FastAPI application (Python + Node helpers) that serves the agentic chatbot APIs without depending on the Next.js runtime.

## Features

- `POST /chatbot/chat` → runs the full agentic workflow (tool planning/execution + AI response). Pass `?stream=1` (or `{ "stream": true }` in the body) to receive newline-delimited streaming updates.
- `GET /chatbot/mcp-status` → reports the health of configured MCP providers.

## Project layout

```
agentic_chatbot_backend/
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
pip install -r agentic_chatbot_backend/requirements.txt
npm install --prefix agentic_chatbot_backend
uvicorn agentic_chatbot_backend.main:app --reload
```

Run the commands from the repository root (or set `NODE_EXECUTABLE` / `MCP_CONFIG_PATH` as needed) so the Node helpers resolve correctly.

### Required environment variables

All variables required by the original Node workflow still apply (e.g. `GOOGLE_GENERATIVE_AI_API_KEY`, `GOOGLE_GEMINI_MODEL`, `GOOGLE_GEMINI_FLASH_MODEL`, MCP endpoints, thinking budgets, etc.).

Optional overrides:

- `NODE_EXECUTABLE` – custom path to the Node runtime if `node` is not on `PATH`.
- `MCP_CONFIG_PATH` – absolute path to an alternative MCP config JSON.
- `NODE_HELPER_TIMEOUT` – seconds to wait for MCP helper scripts (set to `0` for no timeout, default: 15).

## Testing the endpoints

```bash
http POST :8000/chatbot/chat query="Show me the latest costs" messages:='[]'
http GET  :8000/chatbot/mcp-status
```

(`http` is from [httpie](https://httpie.io/); curl or any HTTP client works.)

## Notes

- Streaming mode (`stream=1`) is supported and uses newline-delimited JSON events (`content`, `reasoning`, `meta`, `done`).
- Errors from the Node logic surface as HTTP 502 to make troubleshooting easier.
- Update the files under `node_app/` to change the chatbot behaviour for both routes.

## Docker

Build and run the standalone container from the repo root:

```bash
docker build -f agentic_chatbot_backend/Dockerfile -t agentic-fastapi .
docker run --rm -p 8000:8000 \
  -e GOOGLE_GENERATIVE_AI_API_KEY=... \
  -e GOOGLE_GEMINI_MODEL=gemini-2.5-pro \
  -e GOOGLE_GEMINI_FLASH_MODEL=gemini-2.5-flash \
  agentic-fastapi
```

## Curl - endpoints

Endpoints to test service on localhost

### chat endpoint - streaming enabled

```curl
curl --location 'http://localhost:8088/chatbot/chat?stream=1' \
--header 'accept: */*' \
--header 'accept-language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,la;q=0.6,ta;q=0.5,hi;q=0.4' \
--header 'content-type: application/json' \
--header 'origin: https://dev.dashboard.cloudtuner.ai' \
--header 'priority: u=1, i' \
--header 'referer: https://dev.dashboard.cloudtuner.ai/chatbot' \
--header 'sec-ch-ua: "Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"' \
--header 'sec-ch-ua-mobile: ?0' \
--header 'sec-ch-ua-platform: "macOS"' \
--header 'sec-fetch-dest: empty' \
--header 'sec-fetch-mode: cors' \
--header 'sec-fetch-site: same-origin' \
--header 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36' \
--header 'Cookie: _ga=GA1.1.988417525.1758272138; _gcl_au=1.1.302837750.1758272138; __hstc=254701783.a01e452a2035e13d92d5b609923be0a2.1758272139011.1758272139011.1758272139011.1; hubspotutk=a01e452a2035e13d92d5b609923be0a2; twk_uuid_685beb4581f401190f6c6e62=%7B%22uuid%22%3A%221.1vXXnk8PvYmOYRZfVNI4dfukVYsQl3lJAkU6s1UJ8WDrviPZeWh3gHJQZJ7lnVlyxOGJCIaDnNWvJY6QegVYMlbxtBIQ68O33lCSlwveqQxrBGT61w5mzV5%22%2C%22version%22%3A3%2C%22domain%22%3A%22cloudtuner.ai%22%2C%22ts%22%3A1758272139809%7D; _ga_Q2LE0DJQ7Z=GS2.1.s1758272137$o1$g0$t1758272147$j50$l0$h0' \
--data '{"query":"can you list down all the databases in mongoDB","messages":[{"role":"assistant","content":"Welcome to FinOps Assistant! How can I help with your cloud costs today?"}]}'
```


### status check - mcp-status
```curl


```
