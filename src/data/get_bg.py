import json
from typing import Dict

from pathlib import Path

from ..api.hoyolab import Hoyolab
from ..api.models import GameBgData

file_path = Path("src") / "data" / "bg.json"
BG_MAP: Dict[int, str] = {}


async def save_bg(save: bool = True):
    async with Hoyolab() as hoyolab:
        bg = await hoyolab.get_news_bg()
        if save:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(bg.model_dump(), ensure_ascii=False, indent=4))


def get_bg():
    if not file_path.exists():
        return
    with open(file_path, "r", encoding="utf-8") as f:
        json_data = f.read()
    data = GameBgData.model_validate_json(json_data)
    for bg in data.game_list:
        BG_MAP[int(bg.id)] = bg.bg


get_bg()
