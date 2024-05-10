import os

from dotenv import load_dotenv

load_dotenv()

DEBUG = os.getenv("DEBUG", "True").lower() == "true"
DOMAIN = os.getenv("DOMAIN", "127.0.0.1")
PORT = int(os.getenv("PORT", 8080))
MIYOUSHE = os.getenv("MIYOUSHE", "True").lower() == "true"
HOYOLAB = os.getenv("HOYOLAB", "True").lower() == "true"
BOT = os.getenv("BOT", "True").lower() == "true"
BOT_API_ID = os.getenv("BOT_API_ID")
BOT_API_ID_INT = 0
try:
    BOT_API_ID_INT = int(BOT_API_ID)
except ValueError:
    pass
BOT_API_HASH = os.getenv("BOT_API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MIYOUSHE_HOST = os.getenv("MIYOUSHE_HOST")
HOYOLAB_HOST = os.getenv("HOYOLAB_HOST")
