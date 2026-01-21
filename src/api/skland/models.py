import json
from datetime import datetime
from typing import List, Any, Optional

from pydantic import PrivateAttr, BaseModel, computed_field

GAME_ID_MAP = {
    "arknights": 1,
    "endfield": 3,
}
GAME_STR_MAP = {v: k for k, v in GAME_ID_MAP.items()}
GAME_RECOMMEND_MAP = {
    "arknights": (1, 1),
    "endfield": (3, 12),
}
CHANNEL_MAP = {
    "endfield": "Ark_Endfield",
}


class PostStat(BaseModel):
    commented: int = 0
    reposted: int = 0
    liked: int = 0
    collected: int = 0


class PostTopic(BaseModel):
    id: int
    name: str
    hoyolab: bool = False

    @computed_field
    def url(self) -> str:
        if not self.hoyolab:
            return f"https://www.skland.com/tag?id={self.id}"
        return "https://www.skport.com"


class PostUserInfo(BaseModel):
    id: str
    nickname: str

    avatar: str

    @computed_field
    def url(self) -> str:
        return f"https://www.skland.com/profile?id={self.id}"


class PostInfo(BaseModel):
    _data: dict = PrivateAttr()

    post_id: int
    subject: str

    user: PostUserInfo
    created_at: datetime
    cover: Optional[str]

    format: dict
    text_slice: List[dict]
    link_slice: List[dict]
    image_slice: List[dict]

    game_id: int
    topics: List[PostTopic]
    stat: PostStat

    def __init__(self, _data: dict, **data: Any):
        super().__init__(**data)
        self._data = _data

    @computed_field
    def game_id_str(self) -> str:
        return GAME_STR_MAP.get(self.game_id, "")

    @computed_field
    def url_start(self) -> str:
        return "article?id="

    @computed_field
    def url(self) -> str:
        return f"https://www.skland.com/{self.url_start}{self.post_id}"

    @classmethod
    def paste_data(cls, data: dict, hoyolab: bool = False) -> "PostInfo":
        post = data["item"]
        game_id = post["gameId"]
        post_id = post["id"]
        subject = post["title"]
        image_list = post.get("imageListSlice", [])

        _cover_item = post.get("imageCover")
        _cover = post.get("imageCoverIndex")
        cover = None
        if _cover_item:
            cover = _cover_item.get("url")
        elif _cover:
            cover = {item["id"]: item["url"] for item in image_list}.get(_cover)

        created_at = post["createdAtTs"]
        user = PostUserInfo(**data["user"])  # 用户数据

        content_format = json.loads(post.get("format", "{}"))
        text_slice = post.get("textSlice", [])
        link_slice = post.get("linkSlice", [])

        topics = [PostTopic(**i) for i in data.get("tags", [])]
        stat = PostStat(**data.get("itemRts", {}))
        return PostInfo(
            _data=data,
            hoyolab=hoyolab,
            post_id=post_id,
            user=user,
            subject=subject,
            created_at=created_at,
            cover=cover,
            format=content_format,
            game_id=game_id,
            text_slice=text_slice,
            link_slice=link_slice,
            image_slice=image_list,
            topics=topics,
            stat=stat,
        )

    def __getitem__(self, item):
        return self._data[item]
