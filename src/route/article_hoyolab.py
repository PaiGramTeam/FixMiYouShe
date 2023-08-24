from starlette.requests import Request
from starlette.responses import HTMLResponse

from .base import get_redirect_response
from ..app import app
from ..error import ArticleError, ResponseException
from ..log import logger
from ..render.article_hoyolab import process_article


@app.get("/article/{post_id}")
@app.get("/article/{post_id}/{lang}")
async def parse_hoyo_article(post_id: int, request: Request, lang: str = "zh-cn"):
    try:
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
