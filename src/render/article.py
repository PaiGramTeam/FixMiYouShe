import json
from typing import List, Dict, Callable

from bs4 import BeautifulSoup

from src.api.hyperion import Hyperion
from src.api.i18n import I18n
from src.api.models import (
    PostInfo,
    PostType,
    PostRecommend,
    CHANNEL_MAP,
    CHANNEL_OS_MAP,
    GAME_ID_MAP,
)
from src.data.get_bg import BG_MAP
from src.env import DOMAIN
from src.error import ArticleNotFoundError
from src.log import logger
from src.render.render_data import RenderTemplateData, BaseRenderData, template
from src.utils.common import (
    get_description,
    parse_content,
    parse_stat,
    format_image_url,
)

RECOMMEND_POST_MAP: Dict[str, List[PostRecommend]] = {}


def get_recommend_post(post_info: PostInfo, _: I18n) -> List[PostRecommend]:
    """
    获取推荐文章列表

    Args:
        post_info: 当前文章信息
        _: 国际化对象（未使用）

    Returns:
        List[PostRecommend]: 推荐文章列表
    """
    posts = RECOMMEND_POST_MAP.get(post_info.game_id_str, [])
    if post_info.post_id:
        return [post for post in posts if post.post_id != post_info.post_id]
    return posts


class HyperionRenderData(BaseRenderData):
    """
    Hyperion平台的RenderData实现
    用于处理米游社国内平台的文章渲染数据
    """

    def __init__(self, post_info: PostInfo, i18n: I18n, related_posts_func: Callable):
        """
        初始化HyperionRenderData实例

        Args:
            post_info: 文章信息对象
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
        if self.post_info.view_type == PostType.IMAGE:
            json_data = json.loads(self.post_info.content)
            return json_data.get("describe", "")
        return get_description(self._soup)

    def get_article_content(self) -> str:
        """
        获取处理后的文章内容

        Returns:
            str: 处理后的文章内容
        """
        if (
            self.post_info.view_type == PostType.TEXT
            or self.post_info.view_type == PostType.VIDEO
        ):
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


async def get_post_info(game_id: str, post_id: int):
    """
    获取文章信息

    Args:
        game_id: 游戏ID
        post_id: 文章ID

    Returns:
        PostInfo: 文章信息对象
    """
    gids = GAME_ID_MAP.get(game_id)
    if not gids:
        raise ArticleNotFoundError(game_id, post_id)
    async with Hyperion() as hyperion:
        return await hyperion.get_post_info(gids=gids, post_id=post_id)


async def process_article(game_id: str, post_id: int, i18n: I18n = I18n()) -> str:
    """
    处理文章渲染

    Args:
        game_id: 游戏ID
        post_id: 文章ID
        i18n: 国际化对象

    Returns:
        str: 渲染后的HTML文本
    """
    post_info = await get_post_info(game_id, post_id)
    render_data = HyperionRenderData(post_info, i18n, get_recommend_post)
    template_data = render_data.to_template_data()
    return template.render(**template_data.model_dump())


async def refresh_recommend_posts():
    """
    刷新推荐文章列表
    """
    logger.info("Start to refresh recommend posts")
    async with Hyperion() as hyperion:
        for key, gids in GAME_ID_MAP.items():
            try:
                RECOMMEND_POST_MAP[key] = await hyperion.get_official_recommended_posts(
                    gids
                )
            except Exception as _:
                logger.exception(f"Failed to get recommend posts gids={gids}")
    logger.info("Finish to refresh recommend posts")
