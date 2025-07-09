import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI,Request, APIRouter
from api import router_api
from db.models.migrator import migrate_all
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await asyncio.to_thread(migrate_all)
        print("Database migration completed successfully.", flush=True)
        print("Starting Application...", flush=True)
        yield
    except Exception as e:
        print(f"Error during startup: {e}", flush=True)
        raise
    finally:
        print("Shutting down application...", flush=True)

app = FastAPI(title="Documentation Scraper API", version="1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


chat_agent_router = APIRouter(prefix="/chat-agent")

# Include the router once with all relevant tags
chat_agent_router.include_router(
    router_api.router, 
    tags=[
        "Query", 
        "Document", 
        "Simple Query",
        "Details Analysis",
        "Checklist Analysis", 
        "Cloud Comparison",
        "Cloud Comparison Multiple",
        "Recommendations",
        "Resource Data",
        "Cloud Comparison Filter"
    ]
)

# Include the grouped router in the main app
app.include_router(chat_agent_router)


@app.get("/")
async def root(request: Request):
    """
    Returns a welcome message along with the full request URL.
    """
    return {
        "message": "Welcome to the Documentation Scraper API!",
        "request_url": str(request.url)
    }