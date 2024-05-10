import asyncio

import uvicorn

from fastapi import FastAPI
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .env import DOMAIN, DEBUG, PORT
from .route import get_routes
from .route.base import UserAgentMiddleware
from .services.scheduler import register_scheduler

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


class Web:
    def __init__(self):
        self.web_server = None
        self.web_server_task = None
        self.bot_main_task = None

    @staticmethod
    def init_web():
        if not DEBUG:
            app.add_middleware(
                TrustedHostMiddleware,
                allowed_hosts=[
                    DOMAIN,
                ],
            )
            app.add_middleware(UserAgentMiddleware)
        get_routes()
        register_scheduler(app)

    async def start(self):
        self.init_web()
        self.web_server = uvicorn.Server(
            config=uvicorn.Config(app, host="127.0.0.1", port=PORT)
        )
        server_config = self.web_server.config
        server_config.setup_event_loop()
        if not server_config.loaded:
            server_config.load()
        self.web_server.lifespan = server_config.lifespan_class(server_config)
        try:
            await self.web_server.startup()
        except OSError as e:
            raise SystemExit from e

        if self.web_server.should_exit:
            raise SystemExit from None
        self.web_server_task = asyncio.create_task(self.web_server.main_loop())

    def stop(self):
        if self.web_server_task:
            self.web_server_task.cancel()
        if self.bot_main_task:
            self.bot_main_task.cancel()


web = Web()
