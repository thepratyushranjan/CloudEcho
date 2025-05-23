# -*- coding: utf-8 -*-

from httpx import AsyncClient, HTTPStatusError
from fastapi import HTTPException

from config.config import Config


class CloudTunerServiceRecommendations:
    def __init__(self, client: AsyncClient, org_id: str, api_token: str):
        cfg = Config()
        base = cfg.CLOUDTUNER_API_URL.rstrip("/")
        self.url = f"{base}/organizations/{org_id}/optimizations"
        self.client = client
        self.headers = {"Authorization": f"Bearer {api_token}"}

    async def fetch_recommendations(
        self, limit: int = 3, overview: bool = True
    ) -> dict:
        params = {"limit": limit, "overview": overview}
        try:
            resp = await self.client.get(
                self.url, headers=self.headers, params=params
            )
            return resp.json()
        except HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code, detail=exc.response.text
            )

class CloudTunerServiceResource:
    def __init__(self, client: AsyncClient, api_token: str):
        cfg = Config()
        self.base_url = cfg.CLOUDTUNER_API_URL.rstrip("/")
        self.client   = client
        self.headers  = {"Authorization": f"Bearer {api_token}"}

    async def fetch_resources(self,
                              resource_id: str,
                              details:     bool = True) -> dict:
        url    = f"{self.base_url}/cloud_resources/{resource_id}"
        params = {"details": details}

        try:
            resp = await self.client.get(
                url,
                headers=self.headers,
                params=params
            )
            resp.raise_for_status()
            return resp.json()
        except HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=exc.response.text
            )

