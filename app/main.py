import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, APIRouter
from api import (
    query, document_api, simple_query, details_analysis, 
    checklist_analysis, cloud_comparison_api,
    cloud_comparison_multiple_api,
    recommendations_api,
    resource_api,
    )
from db.models.migrator import migrate_all
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    await asyncio.to_thread(migrate_all)
    yield

app = FastAPI(title="Chat Agent API", version="1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a router group for all chat-agent routes
chat_agent_router = APIRouter(prefix="/chat-agent")

# Include all routes in the group
chat_agent_router.include_router(query.router, tags=["Query"])
chat_agent_router.include_router(document_api.router, tags=["Document"])
chat_agent_router.include_router(simple_query.router, tags=["Simple Query"])

# Include the details analysis routes
chat_agent_router.include_router(details_analysis.router, tags=["Details Analysis"])
chat_agent_router.include_router(checklist_analysis.router, tags=["Checklist Analysis"])

# Include the cloud comparison routes
chat_agent_router.include_router(cloud_comparison_api.router, tags=["Cloud Comparison"])
chat_agent_router.include_router(cloud_comparison_multiple_api.router, tags=["Cloud Comparison Multiple"])

# Include the cloudtuner routes
chat_agent_router.include_router(recommendations_api.router, tags=["Recommendations"])
chat_agent_router.include_router(resource_api.router, tags=["Resource Data"])

# Include the grouped router in the main app
app.include_router(chat_agent_router)

@app.get("/")
async def root(request: Request):
    """
    Returns a welcome message along with the full request URL.
    """
    return {
        "message": "Welcome to the Chat Agent API!",
        "request_url": str(request.url)
    }
