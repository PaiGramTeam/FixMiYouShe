import pytest
from httpx import URL

from src.utils.url import parse_link


@pytest.mark.asyncio
class TestUrl:
    @staticmethod
    async def test_hoyolab_desktop():
        url = URL("https://www.hoyolab.com/article/25091304")
        real = parse_link(url)
        assert real == URL("https://www.hoyolab.pp.ua/article/25091304")

    @staticmethod
    async def test_hoyolab_android():
        url = URL("https://m.hoyolab.com/#/article/25091304?utm_source=sns&utm_medium=twitter&utm_id=2")
        real = parse_link(url)
        assert real == URL("https://www.hoyolab.pp.ua/article/25091304")

    @staticmethod
    async def test_miyoushe_desktop():
        url = URL("https://www.miyoushe.com/sr/article/43966902")
        real = parse_link(url)
        assert real == URL("https://www.miyoushe.pp.ua/sr/article/43966902")

    @staticmethod
    async def test_miyoushe_android():
        url = URL("https://m.miyoushe.com/sr?channel=beta/#/article/43966902")
        real = parse_link(url)
        assert real == URL("https://www.miyoushe.pp.ua/sr/article/43966902")
