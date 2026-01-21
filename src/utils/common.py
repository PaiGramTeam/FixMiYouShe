from typing import Union
from bs4 import BeautifulSoup, Tag, PageElement
from src.api.models import PostInfo, PostStat


def replace_br(text: str) -> str:
    """
    将换行符替换为HTML的<br/>标签

    Args:
        text: 原始文本

    Returns:
        str: 替换后的HTML文本
    """
    if not text:
        return ""
    return text.replace("\n", "<br/>")


def get_description(soup: BeautifulSoup) -> str:
    """
    从BeautifulSoup对象中提取文章描述

    Args:
        soup: BeautifulSoup对象

    Returns:
        str: 文章描述
    """
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
    """
    格式化图片URL，添加图片参数并转换为HTML img标签

    Args:
        url: 原始图片URL

    Returns:
        str: HTML img标签
    """
    from src.api.models import get_images_params

    lower_url = url.lower()
    for ext in (".png", ".jpg", ".jpeg"):
        if lower_url.endswith(ext):
            url += get_images_params()
            break
    return f'<img src="{url}"/>'


def exists_image_url(post_info: PostInfo, url: str) -> bool:
    """
    检查图片URL是否存在于文章的图片列表中

    Args:
        post_info: 文章信息对象
        url: 要检查的图片URL

    Returns:
        bool: 如果存在返回True，否则返回False
    """

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


def parse_tag(tag: Union[Tag, "PageElement"], post_info: PostInfo) -> str:
    """
    解析单个HTML标签，转换为适合渲染的HTML

    Args:
        tag: 要解析的HTML标签
        post_info: 文章信息对象

    Returns:
        str: 解析后的HTML文本
    """
    if tag.name == "a":
        href = tag.get("href")
        if href and href.startswith("/"):
            href = f"https://www.miyoushe.com{href}"
        if href and href.startswith("http"):
            return f'<a href="{href}">{tag.get_text()}</a>'
    elif tag.name == "img":
        from src.api.models import clean_url

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
    """
    解析文章内容的前缀部分，包括封面、标题和视频

    Args:
        _: BeautifulSoup对象（未使用）
        post_info: 文章信息对象

    Returns:
        str: 解析后的HTML文本
    """
    post_text = ""

    if post_info.has_cover and post_info.cover:
        post_text += format_image_url(post_info.cover) + "\n"

    post_text += f"<h1>{post_info.subject}</h1>\n"

    if post_info.video_urls:
        for url in post_info.video_urls:
            post_text += f'<video controls="controls" src="{url}"></video>\n'

    return post_text


def parse_content(soup: BeautifulSoup, post_info: PostInfo) -> str:
    """
    解析完整的文章内容

    Args:
        soup: BeautifulSoup对象
        post_info: 文章信息对象

    Returns:
        str: 解析后的完整HTML文本
    """
    post_text = parse_content_pre(soup, post_info)
    for tag in soup.find("body").children:
        if text := parse_tag(tag, post_info):
            post_text += f"{text}\n"
    return post_text


def parse_stat(stat: PostStat) -> str:
    """
    解析文章统计数据，转换为HTML格式

    Args:
        stat: 文章统计数据对象

    Returns:
        str: 格式化的HTML统计信息
    """
    return (
        f"<p>"
        f"💬 {stat.reply_num} "
        f"🔁 {stat.forward_num} "
        f"❤️ {stat.like_num} "
        f"🔖 {stat.bookmark_num} "
        f"👁️ {stat.view_num} "
        f"</p><br>\n"
    )
