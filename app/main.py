import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI,Request
from api import query, document_api, simple_query, details_analysis, checklist_analysis
from db.models.migrator import migrate_all
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    await asyncio.to_thread(migrate_all)
    yield

app = FastAPI(title="Documentation Scraper API", version="1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(query.router, prefix="/chat-agent", tags=["Query"])
app.include_router(document_api.router, prefix="/chat-agent", tags=["Document"])
app.include_router(simple_query.router, prefix="/chat-agent", tags=["Simple Query"])
app.include_router(details_analysis.router, prefix="/chat-agent", tags=["Details Analysis"])
app.include_router(checklist_analysis.router, prefix="/chat-agent", tags=["Checklist Analysis"])
@app.get("/")
async def root(request: Request):
    """
    Returns a welcome message along with the full request URL.
    """
    return {
        "message": "Welcome to the Documentation Scraper API!",
        "request_url": str(request.url)
    }
