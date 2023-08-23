from fastapi import FastAPI
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .env import DOMAIN, DEBUG
from .route import get_routes
from .route.base import UserAgentMiddleware

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        DOMAIN,
    ],
)
if not DEBUG:
    app.add_middleware(UserAgentMiddleware)
get_routes()
