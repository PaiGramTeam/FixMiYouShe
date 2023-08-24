import asyncio
import uvicorn

from src.app import app
from src.env import PORT, MIYOUSHE, HOYOLAB


async def main():
    if MIYOUSHE:
        from src.render.article import refresh_recommend_posts

        await refresh_recommend_posts()
    if HOYOLAB:
        from src.render.article_hoyolab import refresh_hoyo_recommend_posts

        await refresh_hoyo_recommend_posts()
    web_server = uvicorn.Server(config=uvicorn.Config(app, host="0.0.0.0", port=PORT))
    server_config = web_server.config
    server_config.setup_event_loop()
    if not server_config.loaded:
        server_config.load()
    web_server.lifespan = server_config.lifespan_class(server_config)
    await web_server.startup()
    await web_server.main_loop()


if __name__ == "__main__":
    asyncio.run(main())
