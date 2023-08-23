from uvicorn import run

from src.app import app
from src.env import PORT


if __name__ == "__main__":
    run(app, host="0.0.0.0", port=PORT)
