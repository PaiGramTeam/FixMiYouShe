from typing import Any, List

from pydantic import BaseModel, PrivateAttr

__all__ = (
    "PostStat",
    "PostInfo",
)


class PostStat(BaseModel):
    reply_num: int = 0
    forward_num: int = 0
    like_num: int = 0
    view_num: int = 0
    bookmark_num: int = 0


class PostInfo(BaseModel):
    _data: dict = PrivateAttr()
    post_id: int
    user_uid: int
    subject: str
    image_urls: List[str]
    created_at: int
    video_urls: List[str]

    def __init__(self, _data: dict, **data: Any):
        super().__init__(**data)
        self._data = _data

    @classmethod
    def paste_data(cls, data: dict) -> "PostInfo":
        _data_post = data["post"]
        post = _data_post["post"]
        post_id = post["post_id"]
        subject = post["subject"]
        image_list = _data_post["image_list"]
        image_urls = [image["url"] for image in image_list]
        vod_list = _data_post["vod_list"]
        video_urls = [vod["resolutions"][-1]["url"] for vod in vod_list]
        created_at = post["created_at"]
        user = _data_post["user"]  # 用户数据
        user_uid = user["uid"]  # 用户ID
        return PostInfo(
            _data=data,
            post_id=post_id,
            user_uid=user_uid,
            subject=subject,
            image_urls=image_urls,
            video_urls=video_urls,
            created_at=created_at,
        )

    def __getitem__(self, item):
        return self._data[item]
