from persica.factory.component import AsyncInitializingComponent
from starlette.requests import Request
from starlette.responses import HTMLResponse

from .base import get_redirect_response

from src.core.web_app import WebApp
from src.core.scheduler import TimeScheduler
from src.env import MIYOUSHE
from src.error import ArticleError, ResponseException
from src.log import logger
from src.render.article import process_article, get_post_info, refresh_recommend_posts


class ArticlePlugin(AsyncInitializingComponent):
    def __init__(self, web_app: WebApp, sche: TimeScheduler):
        if not MIYOUSHE:
            return
        web_app.app.add_api_route("/{game_id}/article/{post_id}", self.parse_article)
        web_app.app.add_api_route(
            "/{game_id}/article/{post_id}/json", self.parse_article_json
        )
        sche.scheduler.add_job(refresh_recommend_posts, "cron", minute="0", second="10")

    async def initialize(self):
        if not MIYOUSHE:
            return
        await refresh_recommend_posts()

    @staticmethod
    async def parse_article(game_id: str, post_id: int, request: Request):
        try:
            return HTMLResponse(await process_article(game_id, post_id))
        except ResponseException as e:
            logger.warning(e.message)
            return get_redirect_response(request)
        except ArticleError as e:
            logger.warning(e.msg)
            return get_redirect_response(request)
        except Exception as _:
            logger.exception(
                "Failed to get article game_id[%s] post_id[%s]", game_id, post_id
            )
            return get_redirect_response(request)

    @staticmethod
    async def parse_article_json(game_id: str, post_id: int, request: Request):
        try:
            return await get_post_info(game_id, post_id)
        except ArticleError as e:
            logger.warning(e.msg)
            return get_redirect_response(request)
        except Exception as _:
            logger.exception(
                "Failed to get article game_id[%s] post_id[%s]", game_id, post_id
            )
            return get_redirect_response(request)
