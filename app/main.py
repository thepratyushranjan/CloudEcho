import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from db.models.migrator import migrate_all
from api import query, document_api

@asynccontextmanager
async def lifespan(app: FastAPI):
    await asyncio.to_thread(migrate_all)
    yield

app = FastAPI(title="Documentation Scraper API", version="1.0", lifespan=lifespan)

# Use the app instance to include routers
app.include_router(query.router, prefix="/query", tags=["Query"])
app.include_router(document_api.router, prefix="/document", tags=["Document"])

@app.get("/")
async def root(request: Request):
    return {
        "message": "Welcome to the Documentation Scraper API!",
        "request_url": str(request.url)
    }
