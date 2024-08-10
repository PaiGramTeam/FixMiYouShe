import json
from typing import Union, List, Dict, Callable

from bs4 import BeautifulSoup, Tag, PageElement

from src import template_env
from src.api.hyperion import Hyperion
from src.api.i18n import I18n
from src.api.models import (
    PostStat,
    PostInfo,
    PostType,
    PostRecommend,
    CHANNEL_MAP,
    CHANNEL_OS_MAP,
    GAME_ID_MAP,
    get_images_params,
    clean_url,
)
from src.data.get_bg import BG_MAP
from src.env import DOMAIN, MIYOUSHE
from src.error import ArticleNotFoundError
from src.log import logger
from src.services.scheduler import scheduler

RECOMMEND_POST_MAP: Dict[str, List[PostRecommend]] = {}
template = template_env.get_template("article.jinja2")


def replace_br(text: str) -> str:
    if not text:
        return ""
    return text.replace("\n", "<br/>\n")


def get_description(soup: BeautifulSoup) -> str:
    post_text = ""
    if post_p := soup.find_all("p"):
        for p in post_p:
            t = p.get_text()
            if not t:
                continue
            post_text += f"{replace_br(t)}<br/>\n"
    else:
        post_text += replace_br(soup.get_text())
    return post_text


def format_image_url(url: str) -> str:
    lower_url = url.lower()
    for ext in (".png", ".jpg", ".jpeg"):
        if lower_url.endswith(ext):
            url += get_images_params()
            break
    return f'<img src="{url}"/>'


def exists_image_url(post_info: PostInfo, url: str) -> bool:
    def get_image_key(_url: str) -> str:
        # 获取 url 中 / 后面的内容 _ 前面的内容
        try:
            return _url.split("/")[-1].split("_")[0]
        except IndexError:
            return ""

    if url:
        old_key = get_image_key(url)
        for __url in post_info.image_urls:
            if get_image_key(__url) == old_key:
                return True
    return False


def parse_tag(tag: Union[Tag, PageElement], post_info: PostInfo) -> str:
    if tag.name == "a":
        href = tag.get("href")
        if href and href.startswith("/"):
            href = f"https://www.miyoushe.com{href}"
        if href and href.startswith("http"):
            return f'<a href="{href}">{tag.get_text()}</a>'
    elif tag.name == "img":
        src = clean_url(tag.get("src"))
        if exists_image_url(post_info, src):
            return format_image_url(src)
        return ""
    elif tag.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
        return f"<{tag.name}>{tag.get_text()}</{tag.name}>"
    elif tag.name == "strong":
        return f"<strong>{tag.get_text()}</strong>"
    elif tag.name == "p":
        t = tag.get_text()
        if not t:
            return ""
        post_text = []
        for tag_ in tag.children:
            if text := parse_tag(tag_, post_info):
                post_text.append(text)
        return "<p>" + "\n".join(post_text) + "</p>\n"
    elif tag.name == "iframe":
        src = tag.get("src")
        if src and "https://www.youtube.com" in src:
            return str(tag)
        return ""
    elif tag.name == "div":
        post_text = []
        for tag_ in tag.children:
            if (
                isinstance(tag_, Tag)
                and tag_.name == "div"
                and "ql-image-mask" in tag_["class"]
            ):
                continue
            if text := parse_tag(tag_, post_info):
                post_text.append(text)
        return "\n".join(post_text)
    return replace_br(tag.get_text().strip())


def parse_content_pre(_: BeautifulSoup, post_info: PostInfo) -> str:
    post_text = ""

    if post_info.has_cover and post_info.cover:
        post_text += format_image_url(post_info.cover) + "\n"

    post_text += f"<h1>{post_info.subject}</h1>\n"

    if post_info.video_urls:
        for url in post_info.video_urls:
            post_text += f'<video controls="controls" src="{url}"></video>\n'

    return post_text


def parse_content(soup: BeautifulSoup, post_info: PostInfo) -> str:
    post_text = parse_content_pre(soup, post_info)
    for tag in soup.find("body").children:
        if text := parse_tag(tag, post_info):
            post_text += f"{text}\n"
    return post_text


def parse_stat(stat: PostStat):
    return (
        f"<p>"
        f"💬 {stat.reply_num} "
        f"🔁 {stat.forward_num} "
        f"❤️ {stat.like_num} "
        f"🔖 {stat.bookmark_num} "
        f"👁️ {stat.view_num} "
        f"</p><br>\n"
    )


def get_recommend_post(post_info: PostInfo, _: I18n) -> List[PostRecommend]:
    posts = RECOMMEND_POST_MAP.get(post_info.game_id_str, [])
    if post_info.post_id:
        return [post for post in posts if post.post_id != post_info.post_id]
    return posts


def get_public_data(
    post_info: PostInfo,
    related_posts: Callable[[PostInfo, I18n], List[PostRecommend]],
    i18n: I18n,
) -> Dict:
    channel_map = CHANNEL_OS_MAP if post_info.hoyolab else CHANNEL_MAP
    return {
        "published_time": post_info.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "channel": channel_map.get(post_info.game_id_str, "HSRCN"),
        "stat": parse_stat(post_info.stat),
        "post": post_info,
        "author": post_info["post"]["user"],
        "related_posts": related_posts(post_info, i18n),
        "GAME_BG": BG_MAP.get(post_info.game_id, ""),
        "DOMAIN": DOMAIN,
        "i18n": i18n,
    }


async def process_article_text(
    post_info: PostInfo,
    related_posts: Callable[[PostInfo, I18n], List[PostRecommend]],
    i18n: I18n,
) -> str:
    post_soup = BeautifulSoup(post_info.content, features="lxml")
    return template.render(
        description=get_description(post_soup),
        article=parse_content(post_soup, post_info),
        **get_public_data(post_info, related_posts, i18n),
    )


async def process_article_image(
    post_info: PostInfo,
    related_posts: Callable[[PostInfo, I18n], List[PostRecommend]],
    i18n: I18n,
) -> str:
    json_data = json.loads(post_info.content)
    description = json_data.get("describe", "")
    article = ""
    for image in json_data.get("imgs", []):
        if image in post_info.image_urls:
            article += format_image_url(image)
    if description:
        article += f"<p>{description}</p>\n"
    return template.render(
        description=description,
        article=article,
        **get_public_data(post_info, related_posts, i18n),
    )


async def get_post_info(game_id: str, post_id: int):
    gids = GAME_ID_MAP.get(game_id)
    if not gids:
        raise ArticleNotFoundError(game_id, post_id)
    async with Hyperion() as hyperion:
        return await hyperion.get_post_info(gids=gids, post_id=post_id)


async def process_article(game_id: str, post_id: int, i18n: I18n = I18n()) -> str:
    post_info = await get_post_info(game_id, post_id)
    if post_info.view_type in [PostType.TEXT, PostType.VIDEO]:
        content = await process_article_text(post_info, get_recommend_post, i18n)
    elif post_info.view_type == PostType.IMAGE:
        content = await process_article_image(post_info, get_recommend_post, i18n)
    return content  # noqa


if MIYOUSHE:

    @scheduler.scheduled_job("cron", minute="0", second="10")
    async def refresh_recommend_posts():
        logger.info("Start to refresh recommend posts")
        async with Hyperion() as hyperion:
            for key, gids in GAME_ID_MAP.items():
                try:
                    RECOMMEND_POST_MAP[key] = (
                        await hyperion.get_official_recommended_posts(gids)
                    )
                except Exception as _:
                    logger.exception(f"Failed to get recommend posts gids={gids}")
        logger.info("Finish to refresh recommend posts")
