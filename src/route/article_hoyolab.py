from persica.factory.component import AsyncInitializingComponent
from starlette.requests import Request
from starlette.responses import HTMLResponse

from .base import get_redirect_response

from src.core.web_app import WebApp
from src.core.scheduler import TimeScheduler
from src.env import HOYOLAB
from src.error import ArticleError, ResponseException
from src.log import logger
from src.render.article_hoyolab import (
    process_article,
    get_post_info,
    refresh_hoyo_recommend_posts,
)


class ArticleHoYoPlugin(AsyncInitializingComponent):
    def __init__(self, web_app: WebApp, sche: TimeScheduler):
        if not HOYOLAB:
            return
        web_app.app.add_api_route("/article/{post_id}", self.parse_hoyo_article)
        web_app.app.add_api_route("/article/{post_id}/{lang}", self.parse_hoyo_article)
        sche.scheduler.add_job(
            refresh_hoyo_recommend_posts, "cron", minute="0", second="20"
        )

    async def initialize(self):
        if not HOYOLAB:
            return
        await refresh_hoyo_recommend_posts()

    @staticmethod
    async def parse_hoyo_article(post_id: int, request: Request, lang: str = "zh-cn"):
        try:
            if lang == "json":
                return await get_post_info(post_id, "zh-cn")
            return HTMLResponse(await process_article(post_id, lang))
        except ResponseException as e:
            logger.warning(e.message)
            return get_redirect_response(request)
        except ArticleError as e:
            logger.warning(e.msg)
            return get_redirect_response(request)
        except Exception as _:
            logger.exception(f"Failed to get article {post_id} lang {lang}")
            return get_redirect_response(request)
