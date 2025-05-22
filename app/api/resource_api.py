# -*- coding: utf-8 -*-

from fastapi import APIRouter, Depends, HTTPException
from httpx import AsyncClient

from models.cloudtuner_model.resource_model import ResourceRequest
from utils.http_client import get_async_client
from services.cloudtuner_services import CloudTunerServiceResource

router = APIRouter()

@router.post("/recommndations/resource", response_model=dict)
async def get_resource(
    req: ResourceRequest,
    client: AsyncClient = Depends(get_async_client),
):
    svc = CloudTunerServiceResource(
        client=client,
        api_token=req.api_token
    )
    try:
        return await svc.fetch_resources(
            resource_id=req.resource_id,
            details=req.details
        )
    except HTTPException as exc:
        raise exc
