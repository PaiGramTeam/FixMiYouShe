from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

scheduler = AsyncIOScheduler(timezone="Asia/ShangHai")


def register_scheduler(app: "FastAPI"):
    @app.on_event("startup")
    async def start_event():
        scheduler.start()
