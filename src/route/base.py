from typing import TYPE_CHECKING

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse

if TYPE_CHECKING:
    from starlette.middleware.base import RequestResponseEndpoint
    from starlette.requests import Request
    from starlette.responses import Response


def get_redirect_response(request: "Request") -> RedirectResponse:
    path = request.url.path
    return RedirectResponse(url=f"https://www.miyoushe.com{path}", status_code=302)


class UserAgentMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: "Request", call_next: "RequestResponseEndpoint"
    ) -> "Response":
        user_agent = request.headers.get("User-Agent")
        if (not user_agent) or ("telegram" not in user_agent.lower()):
            return get_redirect_response(request)
        return await call_next(request)
