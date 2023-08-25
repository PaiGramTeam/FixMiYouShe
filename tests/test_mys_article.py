import pytest

from src.error import ArticleNotFoundError
from src.render.article import process_article, refresh_recommend_posts


@pytest.mark.asyncio
class TestMYSArticle:
    @staticmethod
    async def test_refresh_recommend_posts():
        await refresh_recommend_posts()

    @staticmethod
    async def test_get_mys_empty_gids():
        with pytest.raises(ArticleNotFoundError) as e:
            await process_article("", 0)
        assert e is not None

    @staticmethod
    async def test_get_mys_text_article():
        content = await process_article("ys", 42017325)
        assert content is not None
        assert "原神文本整理（二十二）大赤沙海元能尖碑《依稀可以辨认的铭文》" in content
        assert "总之有错可以随时提出，会改的。" in content

    @staticmethod
    async def test_get_mys_image_article():
        content = await process_article("ys", 42776789)
        assert content is not None
        assert "「绘知万物」——原神×知乎 网页答题活动现已开启" in content
        assert (
            "2023/08/25/75276539/f3b7c0ba388fddc603b4a76ea40d189d_6483724820064288526"
            in content
        )
        assert "本次活动资源较大" in content

    @staticmethod
    async def test_get_mys_big_image_article():
        content = await process_article("ys", 42643916)
        assert content is not None
        assert "居民委托" in content
        assert (
            "2023/08/21/100413398/fb66b26e0143da46181d40acfee9a5aa_6628603726056742795"
            in content
        )
        assert "是居民声望委托！！！不是日常任务，更没有成就。" in content

    @staticmethod
    async def test_get_mys_video_article():
        content = await process_article("ys", 42711525)
        assert content is not None
        assert "《原神》枫丹实机画面展示片｜Gamescom 2023" in content
        assert "o4zAkZfsgYrL5akr9FTELBfEpurIEDQPgkGCUA" in content
        assert "《原神》枫丹实机画面展示，踏上新的旅途。" in content
