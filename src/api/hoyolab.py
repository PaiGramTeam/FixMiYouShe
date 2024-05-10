from typing import List

from .hyperionrequest import HyperionRequest
from .models import PostInfo, PostRecommend, HoYoPostMultiLang, GameBgData

__all__ = ("Hoyolab",)


class Hoyolab:
    POST_FULL_URL = "https://bbs-api-os.hoyolab.com/community/post/wapi/getPostFull"
    NEW_LIST_URL = "https://bbs-api-os.hoyolab.com/community/post/wapi/getNewsList"
    NEW_BG_URL = "https://bbs-api-os.hoyolab.com/community/painter/wapi/circle/info"
    LANG = "zh-cn"
    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/90.0.4430.72 Safari/537.36"
    )

    def __init__(self, *args, **kwargs):
        self.client = HyperionRequest(headers=self.get_headers(), *args, **kwargs)

    def get_headers(self, lang: str = LANG):
        return {
            "User-Agent": self.USER_AGENT,
            "Referer": "https://www.hoyolab.com/",
            "X-Rpc-Language": lang,
        }

    async def get_news_recommend(
        self, gids: int, page_size: int = 3, type_: int = 1
    ) -> List[PostRecommend]:
        params = {"gids": gids, "page_size": page_size, "type": type_}
        response = await self.client.get(url=self.NEW_LIST_URL, params=params)
        return [
            PostRecommend(
                post_id=data["post"]["post_id"],
                subject=data["post"]["subject"],
                multi_language_info=HoYoPostMultiLang(
                    **data["post"]["multi_language_info"]
                ),
            )
            for data in response["list"]
        ]

    async def get_post_info(
        self, post_id: int, read: int = 1, scene: int = 1, lang: str = LANG
    ) -> PostInfo:
        params = {"post_id": post_id, "read": read, "scene": scene}
        response = await self.client.get(
            self.POST_FULL_URL, params=params, headers=self.get_headers(lang=lang)
        )
        return PostInfo.paste_data(response, hoyolab=True)

    async def get_news_bg(self) -> GameBgData:
        params = {"with_channel": "1"}
        headers = {
            "x-rpc-app_version": "2.50.0",
            "x-rpc-client_type": "4",
        }
        response = await self.client.get(
            url=self.NEW_BG_URL, params=params, headers=headers
        )
        return GameBgData(**response)

    async def close(self):
        await self.client.shutdown()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
