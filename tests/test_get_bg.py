import pytest

from src.data.get_bg import save_bg


@pytest.mark.asyncio
class TestGetBg:
    @staticmethod
    async def test_get_bg():
        await save_bg(False)
