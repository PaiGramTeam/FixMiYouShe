import pytest

from main import main


@pytest.mark.asyncio
class TestAPP:
    @staticmethod
    async def test_app():
        assert main is not None
