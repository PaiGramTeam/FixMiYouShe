from typing import List

from src.api.models import PostRecommend
from src.api.skland.models import PostInfo
from src.api.skland.skland_request import HyperionRequest


class Skland:
    """米忽悠bbs相关API请求

    该名称来源于米忽悠的安卓BBS包名结尾，考虑到大部分重要的功能确实是在移动端实现了
    """

    POST_FULL_URL = "https://zonai.skland.com/web/v1/item"
    GET_NEW_LIST_URL = "https://zonai.skland.com/web/v1/home/index"

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/90.0.4430.72 Safari/537.36"
    )

    def __init__(self, *args, **kwargs):
        self.client = HyperionRequest(headers=self.get_headers(), *args, **kwargs)

    def get_headers(self):
        return {"User-Agent": self.USER_AGENT}

    async def get_official_recommended_posts(
        self, gids: int, type_id: int
    ) -> List[PostRecommend]:
        return await self.get_new_list_recommended_posts(gids, type_id)

    async def get_post_info(self, post_id: int) -> PostInfo:
        params = {"id": post_id}
        response = await self.client.get(self.POST_FULL_URL, params=params)
        return PostInfo.paste_data(response)

    async def get_new_list(
        self, gids: int, type_id: int, page_size: int = 10, lang: str = ""
    ) -> dict:
        params = {
            "gameId": gids,
            "pageSize": page_size,
            "cateId": type_id,
            "sortType": "2",
        }
        return await self.client.get(url=self.GET_NEW_LIST_URL, params=params)

    async def get_new_list_recommended_posts(
        self, gids: int, type_id: int, page_size: int = 10, lang: str = ""
    ) -> List[PostRecommend]:
        resp = await self.get_new_list(gids, type_id, page_size)
        data = resp["list"]
        return [PostRecommend.parse_skland(i) for i in data]

    async def close(self):
        await self.client.shutdown()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
