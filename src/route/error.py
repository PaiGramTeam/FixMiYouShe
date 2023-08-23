from fastapi.exceptions import RequestValidationError
from starlette.requests import Request

from src.app import app
from src.route.base import get_redirect_response


@app.exception_handler(RequestValidationError)
@app.exception_handler(404)
async def validation_exception_handler(request: "Request", _):
    return get_redirect_response(request)
