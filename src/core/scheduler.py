from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from persica.factory.component import BaseComponent


class TimeScheduler(BaseComponent):
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone="Asia/ShangHai")

    def register_scheduler(self, app: "FastAPI"):
        @app.on_event("startup")
        async def start_event():
            self.scheduler.start()
