from persica.factory.component import AsyncInitializingComponent

from pyrogram import Client

from pathlib import Path

from src.env import BOT, BOT_API_ID_INT, BOT_API_HASH, BOT_TOKEN

data_path = Path("data")
data_path.mkdir(exist_ok=True)


class TelegramBot(AsyncInitializingComponent):
    def __init__(self):
        self.bot = Client(
            "bot",
            api_id=int(BOT_API_ID_INT),
            api_hash=BOT_API_HASH,
            bot_token=BOT_TOKEN,
            workdir="data",
        )

    async def initialize(self):
        if not BOT:
            return
        await self.bot.start()

    async def shutdown(self):
        if not BOT:
            return
        try:
            await self.bot.stop()
        except RuntimeError:
            pass
