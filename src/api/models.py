import json
from datetime import datetime
from enum import Enum
from typing import Any, List, Optional, Dict

from pydantic import BaseModel, PrivateAttr, Field, AliasChoices

GAME_ID_MAP = {"bh3": 1, "ys": 2, "bh2": 3, "wd": 4, "dby": 5, "sr": 6, "zzz": 8}
GAME_STR_MAP = {1: "bh3", 2: "ys", 3: "bh2", 4: "wd", 5: "dby", 6: "sr", 8: "zzz"}
CHANNEL_MAP = {"ys": "yuanshen", "sr": "HSRCN", "zzz": "ZZZNewsletter"}
__all__ = (
    "GAME_ID_MAP",
    "GAME_STR_MAP",
    "CHANNEL_MAP",
    "clean_url",
    "get_images_params",
    "PostStat",
    "PostType",
    "HoYoPostMultiLang",
    "PostInfo",
    "PostRecommend",
)


def clean_url(url: str) -> str:
    if not url:
        return ""
    return url.replace(
        "hoyolab-upload-private.hoyolab.com", "upload-os-bbs.hoyolab.com"
    ).split("?")[0]


def get_images_params(
    resize: int = 600,
    quality: int = 80,
    auto_orient: int = 0,
    interlace: int = 1,
    images_format: str = "jpg",
) -> str:
    """
    image/resize,s_600/quality,q_80/auto-orient,0/interlace,1/format,jpg
    :param resize: 图片大小
    :param quality: 图片质量
    :param auto_orient: 自适应
    :param interlace: 未知
    :param images_format: 图片格式
    :return:
    """
    params = (
        f"image/resize,s_{resize}/quality,q_{quality}/auto-orient,"
        f"{auto_orient}/interlace,{interlace}/format,{images_format}"
    )
    return f"?x-oss-process={params}"


class PostStat(BaseModel):
    reply_num: int = 0
    forward_num: int = Field(
        default=0, validation_alias=AliasChoices("forward_num", "share_num")
    )
    like_num: int = 0
    view_num: int = 0
    bookmark_num: int = 0


class PostTopic(BaseModel):
    id: int
    name: str
    game_id_: int
    hoyolab: bool

    @property
    def url(self) -> str:
        if not self.hoyolab:
            return f"https://www.miyoushe.com/{self.game_id_}/topicDetail/{self.id}"
        return f"https://www.hoyolab.com/topicDetail/{self.id}"


class PostType(int, Enum):
    """帖子类型"""

    TEXT = 1
    IMAGE = 2
    VIDEO = 5


class HoYoPostVideo(BaseModel):
    id: str
    cover: Optional[str]
    url: str

    @property
    def is_youtube(self) -> bool:
        return "www.youtube.com" in self.url


class HoYoPostMultiLang(BaseModel):
    lang_subject: dict


class PostInfo(BaseModel):
    _data: dict = PrivateAttr()
    hoyolab: bool
    post_id: int
    user_uid: int
    subject: str
    image_urls: List[str]
    created_at: datetime
    video_urls: List[str]
    content: str
    cover: Optional[str]
    game_id: int
    topics: List[PostTopic]
    view_type: PostType
    stat: PostStat
    video: Optional[HoYoPostVideo] = None

    def __init__(self, _data: dict, **data: Any):
        super().__init__(**data)
        self._data = _data

    @property
    def game_id_str(self) -> str:
        return GAME_STR_MAP.get(self.game_id, "")

    @property
    def url_start(self) -> str:
        if not self.hoyolab:
            return f"{self.game_id_str}/article"
        return "article"

    @property
    def url_path(self) -> str:
        return f"{self.url_start}/{self.post_id}"

    @property
    def url(self) -> str:
        if not self.hoyolab:
            return f"https://www.miyoushe.com/{self.url_path}"
        return f"https://www.hoyolab.com/{self.url_path}"

    @property
    def author_url(self) -> str:
        author = self._data["post"]["user"]
        if not self.hoyolab:
            return f"https://www.miyoushe.com/{self.game_id_str}/accountCenter/postList?id={author['uid']}"
        return f"https://www.hoyolab.com/accountCenter/postList?id={author['uid']}"

    @staticmethod
    def parse_structured_content(data: List[Dict]) -> str:
        content = []
        for item in data:
            if not item or item.get("insert") is None:
                continue
            insert = item["insert"]
            if isinstance(insert, str):
                if attr := item.get("attributes"):
                    if link := attr.get("link"):
                        content.append(f'<p><a href="{link}">{insert}</a></p>')
                        continue
                content.append(f"<p>{insert}</p>")
            elif isinstance(insert, dict):
                if image := insert.get("image"):
                    content.append(f'<img src="{image}" />')
        return "\n".join(content)

    @classmethod
    def paste_data(cls, data: dict, hoyolab: bool = False) -> "PostInfo":
        _data_post = data["post"]
        post = _data_post["post"]
        post_id = post["post_id"]
        subject = post["subject"]
        image_list = _data_post["image_list"]
        image_urls = [
            image["url"]
            for image in image_list
            if 0.1 <= (image["width"] / image["height"]) <= 10
        ]
        vod_list = _data_post.get("vod_list", [])
        video_urls = [vod["resolutions"][-1]["url"] for vod in vod_list]
        created_at = post["created_at"]
        user = _data_post["user"]  # 用户数据
        user_uid = user["uid"]  # 用户ID
        content = post["content"]
        if (
            hoyolab
            and ("<" not in content)
            and (structured_content := post.get("structured_content"))
        ):
            content = PostInfo.parse_structured_content(json.loads(structured_content))
        cover = post["cover"]
        cover_list = _data_post.get("cover_list", [])
        if (not cover) and cover_list:
            cover = cover_list[0]["url"]
        if (not cover) and image_urls:
            cover = image_urls[0]
        if cover:
            cover = clean_url(cover) + get_images_params()
        game_id = post["game_id"]
        topics = [
            PostTopic(game_id_=game_id, hoyolab=hoyolab, **topic)
            for topic in _data_post["topics"]
        ]
        view_type = PostType(post["view_type"])
        stat = PostStat(**_data_post["stat"])
        video = (
            None
            if _data_post.get("video") is None
            else HoYoPostVideo(**_data_post["video"])
        )
        return PostInfo(
            _data=data,
            hoyolab=hoyolab,
            post_id=post_id,
            user_uid=user_uid,
            subject=subject,
            image_urls=image_urls,
            video_urls=video_urls,
            created_at=created_at,
            content=content,
            cover=cover,
            game_id=game_id,
            topics=topics,
            view_type=view_type,
            stat=stat,
            video=video,
        )

    def __getitem__(self, item):
        return self._data[item]


class PostRecommend(BaseModel):
    post_id: int
    subject: str
    banner: Optional[str] = None
    official_type: Optional[int] = None
    multi_language_info: Optional[HoYoPostMultiLang] = None
