from pathlib import Path
from typing import Optional

import aiofiles

cache_dir = Path("cache")
cache_dir.mkdir(exist_ok=True)


def get_article_cache_file_path(game_id: str, article_id: int) -> Path:
    return cache_dir / f"article_{game_id}_{article_id}.html"


async def get_article_cache_file(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    async with aiofiles.open(path, "r", encoding="utf-8") as f:
        return await f.read()


async def write_article_cache_file(path: Path, content: str) -> None:
    async with aiofiles.open(path, "w", encoding="utf-8") as f:
        await f.write(content)
