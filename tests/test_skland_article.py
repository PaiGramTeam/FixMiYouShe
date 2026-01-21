import pytest

from src.error import ArticleNotFoundError
from src.render.article_skland import process_article, refresh_skland_recommend_posts


@pytest.mark.asyncio
class TestSklandArticle:
    @staticmethod
    async def test_refresh_recommend_posts():
        await refresh_skland_recommend_posts()

    @staticmethod
    async def test_get_skland_empty_post_id():
        with pytest.raises(ArticleNotFoundError) as e:
            await process_article(1)
        assert e is not None

    @staticmethod
    async def test_get_skland_text_article():
        content = await process_article(3583124)
        assert content is not None
        assert "新春联名周边套装将于1月14日补货上架，开启预售" in content
        assert "谢谢大家，提前祝大家新年快乐！" in content

    @staticmethod
    async def test_get_skland_image_article():
        content = await process_article(3587574)
        assert content is not None
        assert "森空岛玩家版主招募公告" in content
        assert "2026/01/13/103/09e424e1a0beb4900d33912bc23a0ac7" in content
        assert "森空岛玩家版主招募问卷" in content
        assert "survey.hypergryph.com" in content

    @staticmethod
    async def test_get_skland_video_article():
        content = await process_article(3594646)
        assert content is not None
        assert "龙泡泡和山团团~热闹非凡的日常生活即将开幕" in content
        assert "2026/01/16/132/b6e2e4cb2eaf59250833e5ec006330b4" in content
        assert "一起度过轻松愉快的日常生活吧~" in content
