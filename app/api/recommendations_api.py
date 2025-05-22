# -*- coding: utf-8 -*-

from fastapi import APIRouter, Depends
from httpx import AsyncClient
from models.cloudtuner_model.recommendation_model import RecommendationRequest
from utils.http_client import get_async_client
from services.cloudtuner_services import CloudTunerServiceRecommendations

router = APIRouter()


@router.post("/recommendations", response_model=dict)
async def get_recommendations(
    req: RecommendationRequest,
    client: AsyncClient = Depends(get_async_client),
):
    svc = CloudTunerServiceRecommendations(
        client=client,
        org_id=req.org_id,
        api_token=req.api_token,
    )
    return await svc.fetch_recommendations(
        limit=req.limit, overview=req.overview
    )
