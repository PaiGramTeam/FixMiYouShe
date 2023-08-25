import pytest

from src.render.article_hoyolab import process_article, refresh_hoyo_recommend_posts


@pytest.mark.asyncio
class TestHoyolabArticle:
    @staticmethod
    async def test_refresh_recommend_posts():
        await refresh_hoyo_recommend_posts()

    @staticmethod
    async def test_get_hoyo_article():
        content = await process_article(21097937, lang="zh")
        assert content is not None
        assert "【有奖活动】枫丹冒险之旅，参与赢原石等奖励" in content
        assert (
            "2023/08/22/cabb57e3aab8e212c035ee5dcca79540_7635259955618222979" in content
        )
        assert "参与资格（仅针对现金奖励）" in content

    @staticmethod
    async def test_get_hoyo_lang_article():
        content = await process_article(21124034, lang="en")
        assert content is not None
        assert (
            '"A Journey of Art and Heritage" - Adeptal Tales: Longquan Celadon | Genshin Impact'
            in content
        )
        assert "The people of Liyue love drinking tea." in content

    @staticmethod
    async def test_get_hoyo_video_article():
        content = await process_article(21124034, "zh-cn")
        assert content is not None
        assert "《原神》「流光拾遗之旅」——仙闻篇·龙泉青瓷" in content
        assert "7Tuq-ritxJE" in content
        assert "璃月人爱喝茶，用青色茶盏盛一碗茶汤，茶香似乎都变得更悠长。" in content

    @staticmethod
    async def test_get_hoyo_big_video_article():
        content = await process_article(17958970, "zh-cn")
        assert content is not None
        assert "Spiral-Abyss-3.6 甘雨暴风雪 & 融甘视频 （面板置放2和3楼）" in content
        assert "0jVRnQHwQ_g" in content
        assert "这次的都是用加HP%加充能和E技能伤害没和伤害直接挂钩的buff" in content
