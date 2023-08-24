import os

from dotenv import load_dotenv

load_dotenv()

DEBUG = os.getenv("DEBUG", "True").lower() == "true"
DOMAIN = os.getenv("DOMAIN", "127.0.0.1")
PORT = int(os.getenv("PORT", 8080))
MIYOUSHE = os.getenv("MIYOUSHE", "True").lower() == "true"
HOYOLAB = os.getenv("HOYOLAB", "True").lower() == "true"
