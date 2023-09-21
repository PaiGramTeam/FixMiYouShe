from starlette.requests import Request
from starlette.responses import Response

from .base import get_redirect_response
from ..api.apk import Apk
from ..app import app
from ..error import ResponseException
from ..log import logger

apk_client = Apk()


@app.get("/app/{apk}")
async def app_download(apk: str, request: Request):
    try:
        if content := await apk_client.get_apk(apk):
            return Response(
                content, media_type="application/vnd.android.package-archive"
            )
        return get_redirect_response(request)
    except ResponseException as e:
        logger.warning(e.message)
        return get_redirect_response(request)
    except Exception as _:
        logger.exception(f"Failed to get apk {apk}")
        return get_redirect_response(request)
