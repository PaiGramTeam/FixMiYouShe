from starlette.requests import Request
from starlette.responses import HTMLResponse

from .base import get_redirect_response
from ..app import app
from ..error import ArticleError, ResponseException
from ..log import logger
from ..render.article import process_article


@app.get("/{game_id}/article/{post_id}")
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
        logger.exception(f"Failed to get article {game_id} {post_id}")
        return get_redirect_response(request)
