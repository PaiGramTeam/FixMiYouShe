from src.api.skland.models import PostInfo, PostStat


def get_images_params(url: str) -> str:
    # style/fullScreen
    # style/fullScreenLandscape
    # style/thirdScreen
    return f"{url}?x-oss-process=style/fullScreen"


def _parse_content(
    post_info: "PostInfo",
    text_map: dict[str, str],
    link_map: dict[str, str],
    image_map: dict[str, str],
) -> tuple[str, set[str]]:
    """
    解析文章内容，将 JSON 格式的内容转换为 HTML 格式

    Args:
        post_info: 文章信息对象，包含格式化的内容数据
        text_map: 文本内容映射，键为 contentId，值为实际文本内容
        link_map: 链接内容映射，键为 linkId，值为实际链接 URL
        image_map: 图片内容映射，键为 imageId，值为实际图片 URL

    Returns:
        tuple[str, set[str]]: 转换后的 HTML 格式内容和使用的图片 ID 集合

    Raises:
        Exception: 解析过程中出现的异常
    """
    try:
        # 获取格式化数据
        format_data = post_info.format
        if not isinstance(format_data, dict):
            return "", set()

        # 获取内容数据列表
        data_list = format_data.get("data", [])
        if not isinstance(data_list, list):
            return "", set()

        # 构建 HTML 内容
        html_content = []
        # 记录使用的图片 ID
        used_image_ids = set()

        for item in data_list:
            item_type = item.get("type")

            # 处理图片类型
            if item_type == "image":
                image_id = item.get("imageId")
                if image_id and image_id in image_map:
                    used_image_ids.add(image_id)
                    image_url = get_images_params(image_map[image_id])
                    html_content.append(
                        f'<img src="{image_url}" alt="Image" style="max-width: 100%; height: auto;">'
                    )

            # 处理段落类型
            elif item_type == "paragraph":
                contents = item.get("contents", [])
                if not isinstance(contents, list):
                    continue

                # 构建段落内容
                paragraph_content = []
                for content in contents:
                    content_type = content.get("type")

                    # 处理文本类型
                    if content_type == "text":
                        content_id = content.get("contentId")
                        if content_id and content_id in text_map:
                            text = text_map[content_id]
                            # 处理文本样式
                            style = []
                            if content.get("bold"):
                                style.append("font-weight: bold;")
                            if content.get("italic"):
                                style.append("font-style: italic;")
                            if content.get("underline"):
                                style.append("text-decoration: underline;")
                            if content.get("del"):
                                style.append("text-decoration: line-through;")
                            if content.get("foregroundColor"):
                                style.append(
                                    f"color: {content.get('foregroundColor')};"
                                )

                            if style:
                                style_str = " ".join(style)
                                paragraph_content.append(
                                    f'<span style="{style_str}">{text}</span>'
                                )
                            else:
                                paragraph_content.append(text)

                    # 处理链接类型
                    elif content_type == "link":
                        content_id = content.get("contentId")
                        link_id = content.get("linkId")
                        if (
                            content_id
                            and content_id in text_map
                            and link_id
                            and link_id in link_map
                        ):
                            text = text_map[content_id]
                            link_url = link_map[link_id]
                            paragraph_content.append(
                                f'<a href="{link_url}" target="_blank">{text}</a>'
                            )

                # 如果段落有内容，添加到 HTML 中
                if paragraph_content:
                    html_content.append(f"<p>{' '.join(paragraph_content)}</p>")
                else:
                    # 空段落添加换行
                    html_content.append("<p>&nbsp;</p>")

        # 合并所有 HTML 内容
        return "\n".join(html_content), used_image_ids

    except Exception as e:
        # 处理异常，返回空字符串和空集合
        print(f"解析内容时出错: {e}")
        return "", set()


def parse_content(
    post_info: "PostInfo",
    text_map: dict[str, str],
    link_map: dict[str, str],
    image_map: dict[str, str],
) -> str:
    """
    解析文章内容，将 JSON 格式的内容转换为 HTML 格式，并将未使用的图片资源添加到最前方

    Args:
        post_info: 文章信息对象，包含格式化的内容数据
        text_map: 文本内容映射，键为 contentId，值为实际文本内容
        link_map: 链接内容映射，键为 linkId，值为实际链接 URL
        image_map: 图片内容映射，键为 imageId，值为实际图片 URL

    Returns:
        str: 转换后的 HTML 格式内容，未使用的图片资源会添加到最前方

    Raises:
        Exception: 解析过程中出现的异常
    """
    try:
        # 首先获取原始的 HTML 内容和已使用的图片 ID 集合
        original_html, used_image_ids = _parse_content(
            post_info, text_map, link_map, image_map
        )

        # 识别未使用的图片资源
        unused_images = []
        for image_id, image_url in image_map.items():
            if image_id not in used_image_ids:
                # 处理图片 URL 并生成 img 标签
                processed_url = get_images_params(image_url)
                img_tag = f'<img src="{processed_url}" alt="Image" style="max-width: 100%; height: auto;">'
                unused_images.append(img_tag)

        # 将未使用的图片资源添加到 HTML 内容最前方
        if unused_images:
            # 合并未使用的图片标签
            unused_images_html = "\n".join(unused_images)
            # 组合最终的 HTML 内容
            final_html = f"{unused_images_html}\n\n{original_html}"
        else:
            # 如果没有未使用的图片，直接返回原始 HTML
            final_html = original_html

        return final_html

    except Exception as e:
        # 处理异常，返回空字符串
        print(f"解析内容时出错: {e}")
        return ""


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
        f"💬 {stat.commented} "
        f"🔁 {stat.reposted} "
        f"❤️ {stat.liked} "
        f"🔖 {stat.collected} "
        f"</p><br>\n"
    )
