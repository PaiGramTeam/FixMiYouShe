from datetime import datetime
from typing import Union, List

from bs4 import BeautifulSoup, Tag, PageElement

from src import template_env
from src.api.hyperion import Hyperion
from src.api.models import PostStat
from src.error import ArticleNotFoundError
from src.services.cache import (
    get_article_cache_file_path,
    get_article_cache_file,
    write_article_cache_file,
)
from src.services.scheduler import add_delete_file_job

GAME_ID_MAP = {"bh3": 1, "ys": 2, "bh2": 3, "wd": 4, "dby": 5, "sr": 6, "zzz": 8}
CHANNEL_MAP = {"ys": "yuanshen", "sr": "HSRCN", "zzz": "ZZZNewsletter"}
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


def parse_tag(tag: Union[Tag, PageElement]) -> str:
    if tag.name == "a":
        href = tag.get("href")
        if href and href.startswith("/"):
            href = f"https://www.miyoushe.com{href}"
        if href and href.startswith("http"):
            return f'<a href="{href}">{tag.get_text()}</a>'
    elif tag.name == "img":
        return f"<p>{str(tag)}</p>"
    elif tag.name == "p":
        t = tag.get_text()
        if not t:
            return ""
        post_text = []
        for tag_ in tag.children:
            if text := parse_tag(tag_):
                post_text.append(text)
        return "\n".join(post_text)
    elif tag.name == "div":
        post_text = []
        for tag_ in tag.children:
            if text := parse_tag(tag_):
                post_text.append(text)
        return "\n".join(post_text)
    text = tag.get_text().strip()
    if text:
        return f"<p>{replace_br(text)}</p>"


def parse_content(soup: BeautifulSoup, title: str, video_urls: List[str]) -> str:
    post_text = f"<h1>{title}</h1>\n"
    if video_urls:
        for url in video_urls:
            post_text += f'<video controls="controls" src="{url}"></video>\n'
    for tag in soup.find("body").children:
        if text := parse_tag(tag):
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


async def process_article(game_id: str, post_id: int) -> str:
    path = get_article_cache_file_path(game_id, post_id)
    if content := await get_article_cache_file(path):
        return content
    gids = GAME_ID_MAP.get(game_id)
    if not gids:
        raise ArticleNotFoundError(game_id, post_id)
    hyperion = Hyperion()
    try:
        post_info = await hyperion.get_post_info(gids=gids, post_id=post_id)
    finally:
        await hyperion.close()
    post_data = post_info["post"]["post"]
    post_soup = BeautifulSoup(post_data["content"], features="lxml")
    author_data = post_info["post"]["user"]
    content = template.render(
        url=f"https://www.miyoushe.com/{game_id}/article/{post_id}",
        description=get_description(post_soup),
        published_time=datetime.fromtimestamp(post_info.created_at).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
        channel=CHANNEL_MAP.get(game_id, "HSRCN"),
        article=parse_content(post_soup, post_info.subject, post_info.video_urls),
        stat=parse_stat(PostStat(**post_info["post"]["stat"])),
        post=post_data,
        author=author_data,
    )
    await write_article_cache_file(path, content)
    add_delete_file_job(path)
    return content
