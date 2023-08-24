from typing import List

from .hyperionrequest import HyperionRequest
from .models import PostInfo, PostRecommend

__all__ = ("Hyperion",)


class Hyperion:
    """米忽悠bbs相关API请求

    该名称来源于米忽悠的安卓BBS包名结尾，考虑到大部分重要的功能确实是在移动端实现了
    """

    POST_FULL_URL = "https://bbs-api.miyoushe.com/post/wapi/getPostFull"
    GET_OFFICIAL_RECOMMENDED_POSTS_URL = (
        "https://bbs-api.miyoushe.com/post/wapi/getOfficialRecommendedPosts"
    )

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/90.0.4430.72 Safari/537.36"
    )

    def __init__(self, *args, **kwargs):
        self.client = HyperionRequest(headers=self.get_headers(), *args, **kwargs)

    def get_headers(self, referer: str = "https://www.miyoushe.com/ys/"):
        return {"User-Agent": self.USER_AGENT, "Referer": referer}

    async def get_official_recommended_posts(self, gids: int) -> List[PostRecommend]:
        params = {"gids": gids}
        response = await self.client.get(
            url=self.GET_OFFICIAL_RECOMMENDED_POSTS_URL, params=params
        )
        return [PostRecommend(**data) for data in response["list"]]

    async def get_post_info(self, gids: int, post_id: int, read: int = 1) -> PostInfo:
        params = {"gids": gids, "post_id": post_id, "read": read}
        response = await self.client.get(self.POST_FULL_URL, params=params)
        return PostInfo.paste_data(response)

    async def close(self):
        await self.client.shutdown()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
