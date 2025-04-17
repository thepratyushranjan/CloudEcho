import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI,Request
from api import query, document_api, simple_query, details_analysis
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
app.include_router(query.router, prefix="/query", tags=["Query"])
app.include_router(document_api.router, prefix="/document", tags=["Document"])
app.include_router(simple_query.router, prefix="/simple-query", tags=["Simple Query"])
app.include_router(details_analysis.router, prefix="/details-analysis", tags=["Details Analysis"])
@app.get("/")
async def root(request: Request):
    """
    Returns a welcome message along with the full request URL.
    """
    return {
        "message": "Welcome to the Documentation Scraper API!",
        "request_url": str(request.url)
    }
