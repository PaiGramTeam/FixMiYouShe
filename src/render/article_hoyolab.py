import json
from typing import Dict, List, Callable

from src.api.hoyolab import Hoyolab
from src.api.i18n import I18n, i18n_alias
from src.api.models import PostRecommend, PostType, PostInfo
from src.env import HOYOLAB
from src.log import logger
from src.render.article import (
    process_article_text,
    process_article_image,
    template,
    get_public_data,
)
from src.services.scheduler import scheduler

GAME_ID_MAP = {"bh3": 1, "ys": 2, "wd": 4, "dby": 5, "sr": 6, "zzz": 8}
RECOMMEND_POST_MAP: Dict[int, List[PostRecommend]] = {}


def get_recommend_post(post_info: PostInfo, i18n: I18n) -> List[PostRecommend]:
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


async def process_article_video(
    post_info: PostInfo,
    related_posts: Callable[[PostInfo, I18n], List[PostRecommend]],
    i18n: I18n,
) -> str:
    json_data = json.loads(post_info.content)
    description = json_data.get("describe", "")
    article = ""
    if post_info.video and post_info.video.is_youtube:
        article += f'<iframe allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen="true" border="0" frameborder="0" framespacing="0" scrolling="no" src="{post_info.video.url}"></iframe>\n'
    if description:
        article += f"<p>{description}</p>\n"
    return template.render(
        description=description,
        article=article,
        **get_public_data(post_info, related_posts, i18n),
    )


async def get_post_info(post_id: int, lang: str):
    async with Hoyolab() as hoyolab:
        return await hoyolab.get_post_info(post_id=post_id, lang=lang)


async def process_article(post_id: int, lang: str) -> str:
    try:
        i18n = I18n(i18n_alias.get(lang))
        if not i18n:
            i18n = I18n(lang)
    except ValueError:
        i18n = I18n()
    post_info = await get_post_info(post_id, i18n.lang.value)
    if post_info.view_type == PostType.TEXT:
        content = await process_article_text(post_info, get_recommend_post, i18n)
    elif post_info.view_type == PostType.IMAGE:
        content = await process_article_image(post_info, get_recommend_post, i18n)
    elif post_info.view_type == PostType.VIDEO:
        content = await process_article_video(post_info, get_recommend_post, i18n)
    return content  # noqa


if HOYOLAB:

    @scheduler.scheduled_job("cron", minute="0", second="10")
    async def refresh_hoyo_recommend_posts():
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
