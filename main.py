from fastapi import FastAPI,Request
from app.api import query, document_api

app = FastAPI(title="Documentation Scraper API", version="1.0")

app.include_router(query.router, prefix="/query", tags=["Query"])
app.include_router(document_api.router, prefix="/document", tags=["Document"])

@app.get("/")
async def root(request: Request):
    """
    Returns a welcome message along with the full request URL.
    """
    return {
        "message": "Welcome to the Documentation Scraper API!",
        "request_url": str(request.url)
    }