from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from src.api.models import PostInfo, PostType, PostRecommend


class RenderTemplateData(BaseModel):
    """
    渲染模板所需的数据模型
    用于确保template.render()方法的数据结构一致性和类型安全性
    """

    description: str
    article: str
    published_time: str
    channel: str
    stat: str
    post: PostInfo
    author: Dict[str, Any]
    related_posts: List[PostRecommend]
    GAME_BG: str
    DOMAIN: str
    i18n: Any


class RenderData(ABC):
    """
    RenderData抽象接口，定义统一的数据结构和访问方法
    用于将数据处理与视图渲染解耦，提升扩展性
    """

    def __init__(self, post_info: PostInfo):
        """
        初始化RenderData实例

        Args:
            post_info: 原始文章信息对象
        """
        self._post_info = post_info
        self._processed_data = {}

    @property
    def post_info(self) -> PostInfo:
        """
        获取原始文章信息

        Returns:
            PostInfo: 原始文章信息对象
        """
        return self._post_info

    @property
    def processed_data(self) -> Dict[str, Any]:
        """
        获取处理后的数据

        Returns:
            Dict[str, Any]: 处理后的数据字典
        """
        return self._processed_data

    @abstractmethod
    def get_description(self) -> str:
        """
        获取文章描述

        Returns:
            str: 文章描述
        """
        pass

    @abstractmethod
    def get_article_content(self) -> str:
        """
        获取处理后的文章内容

        Returns:
            str: 处理后的文章内容
        """
        pass

    @abstractmethod
    def get_public_data(self) -> Dict[str, Any]:
        """
        获取公共渲染数据

        Returns:
            Dict[str, Any]: 公共渲染数据字典
        """
        pass

    @abstractmethod
    def get_post_type(self) -> PostType:
        """
        获取文章类型

        Returns:
            PostType: 文章类型
        """
        pass

    def process(self) -> None:
        """
        处理数据的主方法，会调用各个具体的数据处理方法
        子类可以重写此方法以添加自定义处理逻辑
        """
        # 可以在这里添加通用的数据处理逻辑
        pass

    @abstractmethod
    def to_template_data(self) -> RenderTemplateData:
        """
        生成渲染模板所需的数据模型实例

        Returns:
            RenderTemplateData: 渲染模板数据模型实例
        """
        pass


class BaseRenderData(RenderData):
    """
    基础RenderData实现，提供通用的数据处理逻辑
    适用于大多数平台的基础渲染需求
    """

    def __init__(self, post_info: PostInfo, i18n):
        """
        初始化BaseRenderData实例

        Args:
            post_info: 原始文章信息对象
            i18n: 国际化对象
        """
        super().__init__(post_info)
        self._i18n = i18n

    @property
    def i18n(self):
        """
        获取国际化对象

        Returns:
            Any: 国际化对象
        """
        return self._i18n

    def get_post_type(self) -> PostType:
        """
        获取文章类型

        Returns:
            PostType: 文章类型
        """
        return self._post_info.view_type


class HoyolabRenderData(BaseRenderData):
    """
    米游社(hoyolab)平台的RenderData实现
    扩展了BaseRenderData，添加了米游社特定的数据处理逻辑
    """

    def __init__(self, post_info: PostInfo, i18n, related_posts_func):
        """
        初始化HoyolabRenderData实例

        Args:
            post_info: 原始文章信息对象
            i18n: 国际化对象
            related_posts_func: 获取相关文章的函数
        """
        super().__init__(post_info, i18n)
        self._related_posts_func = related_posts_func

    def process(self) -> None:
        """
        处理米游社特定数据
        """
        super().process()
        # 可以在这里添加米游社特定的数据处理逻辑
        pass
