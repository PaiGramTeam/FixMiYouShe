from typing import Dict, List, Callable

from src.api.i18n import I18n
from src.api.models import PostRecommend
from src.api.skland.skland import Skland
from src.api.skland.models import PostInfo, GAME_RECOMMEND_MAP, CHANNEL_MAP
from src.error import ResponseException, ArticleNotFoundError
from src.log import logger
from src.render.render_data import RenderTemplateData, BaseRenderData, template_skland
from src.env import SKLAND_DOMAIN
from src.utils.skland import parse_stat, parse_content

RECOMMEND_POST_MAP: Dict[int, List[PostRecommend]] = {}


def get_recommend_post(post_info: PostInfo, _: I18n) -> List[PostRecommend]:
    """
    获取森空岛平台的推荐文章列表

    Args:
        post_info: 当前文章信息
        _: 国际化对象

    Returns:
        List[PostRecommend]: 推荐文章列表
    """
    posts = RECOMMEND_POST_MAP.get(post_info.game_id, [])
    return [post for post in posts if post.post_id != post_info.post_id]


class SklandRenderData(BaseRenderData):
    """
    森空岛平台的RenderData实现
    扩展了BaseRenderData，添加了森空岛特定的数据处理逻辑
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
        self.text_map = {item["id"]: item["c"] for item in self.post_info.text_slice}
        self.link_map = {item["id"]: item["c"] for item in self.post_info.link_slice}
        self.image_map = {
            item["id"]: item["url"] for item in self.post_info.image_slice
        }

    @property
    def post_info(self) -> "PostInfo":
        return self._post_info

    def get_description(self) -> str:
        """
        获取文章描述

        Returns:
            str: 文章描述
        """
        post = self.post_info["item"]
        caption = post.get("caption", [])
        if not caption:
            return ""
        text = ""
        for cap in caption:
            if cap.get("type") == "text":
                text += self.text_map.get(cap.get("id"), "")
        return text

    def get_article_content(self) -> str:
        """
        获取处理后的文章内容

        Returns:
            str: 处理后的文章内容
        """
        return parse_content(
            self.post_info, self.text_map, self.link_map, self.image_map
        )

    def get_public_data(self) -> Dict[str, any]:
        """
        获取公共渲染数据

        Returns:
            Dict[str, any]: 公共渲染数据字典
        """
        channel_map = CHANNEL_MAP
        return {
            "published_time": self.post_info.created_at.strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ"
            ),
            "channel": channel_map.get(self.post_info.game_id_str, "Ark_Endfield"),
            "stat": parse_stat(self.post_info.stat),
            "post": self.post_info,
            "author": self.post_info.user.model_dump(),
            "related_posts": self._related_posts_func(self.post_info, self.i18n),
            "DOMAIN": SKLAND_DOMAIN,
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
            GAME_BG="",
            DOMAIN=public_data["DOMAIN"],
            i18n=public_data["i18n"],
        )


async def get_post_info(post_id: int):
    """
    获取森空岛文章信息

    Args:
        post_id: 文章ID

    Returns:
        PostInfo: 文章信息对象
    """
    try:
        async with Skland() as skland:
            return await skland.get_post_info(post_id=post_id)
    except ResponseException as exc:
        if exc.code == 1019:
            raise ArticleNotFoundError("skland", post_id) from exc
        raise


async def process_article(
    post_id: int, lang: str = "zh-cn", i18n: I18n = I18n()
) -> str:
    """
    处理森空岛文章渲染

    Args:
        post_id: 文章ID
        lang: 语言代码
        i18n: 国际化对象

    Returns:
        str: 渲染后的HTML文本
    """
    post_info = await get_post_info(post_id)

    render_data = SklandRenderData(post_info, i18n, get_recommend_post)
    template_data = render_data.to_template_data()
    return template_skland.render(**template_data.model_dump())


async def refresh_skland_recommend_posts():
    """
    刷新森空岛推荐文章列表
    """
    logger.info("Start to refresh skland recommend posts")
    async with Skland() as skland:
        for gid, type_id in GAME_RECOMMEND_MAP.values():
            temp = []
            try:
                temp.extend(
                    await skland.get_official_recommended_posts(gid, type_id=type_id)
                )
            except Exception as _:
                logger.exception(
                    f"Failed to get skland recommend posts gids={gid} type={type_id}"
                )
            RECOMMEND_POST_MAP[gid] = temp
    logger.info("Finish to refresh skland recommend posts")
