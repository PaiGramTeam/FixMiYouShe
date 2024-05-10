from typing import Optional

from httpx import AsyncClient

from src.api.models import PostInfo
from src.env import API_TOKEN

client = AsyncClient(
    headers=(
        {
            "API-TOKEN": API_TOKEN,
        }
        if API_TOKEN
        else {}
    )
)


async def get_post_info(url: str) -> Optional[PostInfo]:
    real_url = f"{url}json" if url.endswith("/") else f"{url}/json"
    req = await client.get(real_url)
    if req.status_code != 200:
        return None
    return PostInfo(_data={}, **req.json())
