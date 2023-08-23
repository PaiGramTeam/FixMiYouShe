import datetime
from pathlib import Path

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler(timezone="Asia/ShangHai")
if not scheduler.running:
    scheduler.start()


async def delete_file(path: Path):
    path = Path(path)
    if path.exists():
        path.unlink(missing_ok=True)


def add_delete_file_job(path: Path, delete_seconds: int = 3600):
    scheduler.add_job(
        delete_file,
        "date",
        id=f"{hash(path)}|delete_file",
        name=f"{hash(path)}|delete_file",
        args=[path],
        run_date=datetime.datetime.now(pytz.timezone("Asia/Shanghai"))
        + datetime.timedelta(seconds=delete_seconds),
        replace_existing=True,
    )
