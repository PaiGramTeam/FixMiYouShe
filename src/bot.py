from pyrogram import Client

from pathlib import Path

from .env import BOT_API_ID_INT, BOT_API_HASH, BOT_TOKEN

data_path = Path("data")
data_path.mkdir(exist_ok=True)

bot = Client(
    "bot",
    api_id=int(BOT_API_ID_INT),
    api_hash=BOT_API_HASH,
    bot_token=BOT_TOKEN,
    workdir="data",
    plugins=dict(root="src/plugins"),
)
