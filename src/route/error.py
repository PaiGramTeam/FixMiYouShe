from fastapi.exceptions import RequestValidationError
from persica.factory.component import BaseComponent
from starlette.requests import Request

from src.core.web_app import WebApp
from src.route.base import get_redirect_response


class ErrorRoutePlugin(BaseComponent):
    def __init__(self, web_app: WebApp):
        web_app.app.add_exception_handler(
            RequestValidationError, self.validation_exception_handler
        )
        web_app.app.add_exception_handler(404, self.validation_exception_handler)

    @staticmethod
    async def validation_exception_handler(request: "Request", _):
        return get_redirect_response(request)
