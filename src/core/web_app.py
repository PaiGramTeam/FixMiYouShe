import asyncio

import uvicorn

from fastapi import FastAPI
from persica.factory.component import AsyncInitializingComponent
from starlette.middleware.trustedhost import TrustedHostMiddleware

from src.core.scheduler import TimeScheduler
from src.env import DOMAIN, DEBUG, PORT


class WebApp(AsyncInitializingComponent):
    def __init__(self, scheduler: TimeScheduler):
        self.app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
        scheduler.register_scheduler(self.app)
        self.web_server = None
        self.web_server_task = None

    def init_web(self):
        if not DEBUG:
            self.app.add_middleware(
                TrustedHostMiddleware,
                allowed_hosts=[
                    DOMAIN,
                ],
            )

    async def start(self):
        self.init_web()
        self.web_server = uvicorn.Server(
            config=uvicorn.Config(self.app, host="0.0.0.0", port=PORT)
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

    async def initialize(self):
        await self.start()

    async def shutdown(self):
        self.stop()
        if self.web_server:
            try:
                await self.web_server.shutdown()
            except AttributeError:
                pass
