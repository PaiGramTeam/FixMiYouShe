import json
from typing import Dict, List, Callable

from bs4 import BeautifulSoup

from src.api.hoyolab import Hoyolab
from src.api.i18n import I18n, i18n_alias
from src.api.models import PostRecommend, PostType, PostInfo, GAME_ID_MAP
from src.log import logger
from src.render.render_data import RenderTemplateData, BaseRenderData, template
from src.utils.common import (
    get_description,
    parse_content,
    parse_stat,
    format_image_url,
)
from src.data.get_bg import BG_MAP
from src.env import DOMAIN
from src.api.models import CHANNEL_MAP, CHANNEL_OS_MAP

RECOMMEND_POST_MAP: Dict[int, List[PostRecommend]] = {}


def get_recommend_post(post_info: PostInfo, i18n: I18n) -> List[PostRecommend]:
    """
    获取米游社平台的推荐文章列表

    Args:
        post_info: 当前文章信息
        i18n: 国际化对象

    Returns:
        List[PostRecommend]: 推荐文章列表
    """
    posts = RECOMMEND_POST_MAP.get(post_info.game_id, [])
    return [
        PostRecommend(
            post_id=post.post_id,
            subject=(
                post.multi_language_info.lang_subject.get(i18n.lang.value, post.subject)
                if post.multi_language_info
                else post.subject
            ),
        )
        for post in posts
        if post.post_id != post_info.post_id
    ]


class HoyolabRenderData(BaseRenderData):
    """
    米游社(hoyolab)平台的RenderData实现
    扩展了BaseRenderData，添加了米游社特定的数据处理逻辑
    """

    def __init__(self, post_info: PostInfo, i18n: I18n, related_posts_func: Callable):
        """
        初始化HoyolabRenderData实例

        Args:
            post_info: 原始文章信息对象
            i18n: 国际化对象
            related_posts_func: 获取相关文章的函数
        """
        super().__init__(post_info, i18n)
        self._related_posts_func = related_posts_func
        self._soup = (
            BeautifulSoup(self.post_info.content, features="lxml")
            if self.post_info.content
            else None
        )

    def get_description(self) -> str:
        """
        获取文章描述

        Returns:
            str: 文章描述
        """
        if (
            self.post_info.view_type == PostType.IMAGE
            or self.post_info.view_type == PostType.VIDEO
        ):
            json_data = json.loads(self.post_info.content)
            return json_data.get("describe", "")
        return get_description(self._soup)

    def get_article_content(self) -> str:
        """
        获取处理后的文章内容

        Returns:
            str: 处理后的文章内容
        """
        if self.post_info.view_type == PostType.TEXT:
            return parse_content(self._soup, self.post_info)
        elif self.post_info.view_type == PostType.IMAGE:
            json_data = json.loads(self.post_info.content)
            article = ""
            for image in json_data.get("imgs", []):
                if image in self.post_info.image_urls:
                    article += format_image_url(image)
            if description := json_data.get("describe", ""):
                article += f"<p>{description}</p>\n"
            return article
        elif self.post_info.view_type == PostType.VIDEO:
            json_data = json.loads(self.post_info.content)
            article = ""
            if self.post_info.video:
                article += self.post_info.video.html
            if description := json_data.get("describe", ""):
                article += f"<p>{description}</p>\n"
            return article
        return ""

    def get_public_data(self) -> Dict[str, any]:
        """
        获取公共渲染数据

        Returns:
            Dict[str, any]: 公共渲染数据字典
        """
        channel_map = CHANNEL_OS_MAP if self.post_info.hoyolab else CHANNEL_MAP
        return {
            "published_time": self.post_info.created_at.strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ"
            ),
            "channel": channel_map.get(self.post_info.game_id_str, "HSRCN"),
            "stat": parse_stat(self.post_info.stat),
            "post": self.post_info,
            "author": self.post_info["post"]["user"],
            "related_posts": self._related_posts_func(self.post_info, self.i18n),
            "GAME_BG": BG_MAP.get(self.post_info.game_id, ""),
            "DOMAIN": DOMAIN,
            "i18n": self.i18n,
        }

    def to_template_data(self) -> RenderTemplateData:
        """
        生成渲染模板所需的数据模型实例

        Returns:
            RenderTemplateData: 渲染模板数据模型实例
        """
        public_data = self.get_public_data()
        return RenderTemplateData(
            description=self.get_description(),
            article=self.get_article_content(),
            published_time=public_data["published_time"],
            channel=public_data["channel"],
            stat=public_data["stat"],
            post=public_data["post"],
            author=public_data["author"],
            related_posts=public_data["related_posts"],
            GAME_BG=public_data["GAME_BG"],
            DOMAIN=public_data["DOMAIN"],
            i18n=public_data["i18n"],
        )


async def get_post_info(post_id: int, lang: str):
    """
    获取米游社文章信息

    Args:
        post_id: 文章ID
        lang: 语言代码

    Returns:
        PostInfo: 文章信息对象
    """
    async with Hoyolab() as hoyolab:
        return await hoyolab.get_post_info(post_id=post_id, lang=lang)


async def process_article(post_id: int, lang: str) -> str:
    """
    处理米游社文章渲染

    Args:
        post_id: 文章ID
        lang: 语言代码

    Returns:
        str: 渲染后的HTML文本
    """
    try:
        i18n = I18n(i18n_alias.get(lang))
        if not i18n:
            i18n = I18n(lang)
    except ValueError:
        i18n = I18n()
    post_info = await get_post_info(post_id, i18n.lang.value)

    # 使用HoyolabRenderData处理所有类型的文章
    render_data = HoyolabRenderData(post_info, i18n, get_recommend_post)
    template_data = render_data.to_template_data()
    return template.render(**template_data.model_dump())


async def refresh_hoyo_recommend_posts():
    """
    刷新米游社推荐文章列表
    """
    logger.info("Start to refresh hoyolab recommend posts")
    async with Hoyolab() as hoyolab:
        for gids in GAME_ID_MAP.values():
            temp = []
            for k in (1, 2, 3):
                try:
                    temp.extend(await hoyolab.get_news_recommend(gids, type_=k))
                except Exception as _:
                    logger.exception(
                        f"Failed to get recommend posts gids={gids} type={k}"
                    )
            RECOMMEND_POST_MAP[gids] = temp
    logger.info("Finish to refresh hoyolab recommend posts")
