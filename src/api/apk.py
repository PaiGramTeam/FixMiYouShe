from pathlib import Path
from typing import Optional

from src.api.hyperionrequest import HyperionRequest

cache = Path("cache")
apk_data = cache / "apk"
cache.mkdir(exist_ok=True)
apk_data.mkdir(exist_ok=True)


class Apk:
    def __init__(self):
        self.client = HyperionRequest()

    @staticmethod
    async def get_apk_from_cache(apk: str) -> Optional[bytes]:
        path = apk_data / apk
        if path.exists():
            return path.read_bytes()
        return None

    async def get_apk(self, apk: str):
        if content := await self.get_apk_from_cache(apk):
            return content
        resp = await self.client.get(
            f"https://download-bbs.miyoushe.com/app/{apk}", de_json=False
        )
        if resp.status_code == 200:
            path = apk_data / apk
            path.write_bytes(resp.content)
            return resp.content
        return None
