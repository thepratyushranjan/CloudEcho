# -*- coding: utf-8 -*-

from httpx import AsyncClient, Timeout
from typing import AsyncGenerator

async def get_async_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Dependency that yields an HTTPX AsyncClient.
    """
    client = AsyncClient(timeout=Timeout(10.0))
    try:
        yield client
    finally:
        await client.aclose()
