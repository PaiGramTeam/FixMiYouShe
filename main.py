import asyncio

from signal import signal as signal_fn, SIGINT, SIGTERM, SIGABRT

from src.app import web
from src.bot import bot
from src.env import MIYOUSHE, HOYOLAB, BOT


async def idle():
    task = None

    def signal_handler(_, __):
        if web.web_server_task:
            web.web_server_task.cancel()
        task.cancel()

    for s in (SIGINT, SIGTERM, SIGABRT):
        signal_fn(s, signal_handler)

    while True:
        task = asyncio.create_task(asyncio.sleep(600))
        web.bot_main_task = task
        try:
            await task
        except asyncio.CancelledError:
            break


async def main():
    if MIYOUSHE:
        from src.render.article import refresh_recommend_posts

        await refresh_recommend_posts()
    if HOYOLAB:
        from src.render.article_hoyolab import refresh_hoyo_recommend_posts

        await refresh_hoyo_recommend_posts()
    await web.start()
    if BOT:
        await bot.start()
    try:
        await idle()
    finally:
        if BOT:
            try:
                await bot.stop()
            except RuntimeError:
                pass
        if web.web_server:
            try:
                await web.web_server.shutdown()
            except AttributeError:
                pass


if __name__ == "__main__":
    asyncio.run(main())
