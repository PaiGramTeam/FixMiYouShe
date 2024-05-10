from typing import List, Optional

from pyrogram.types import (
    InputTextMessageContent,
    InlineQueryResultArticle,
    InlineQuery,
    InlineQueryResult,
    InlineQueryResultPhoto,
    InlineQueryResultDocument,
)

from .start import get_test_button
from ..api.bot_request import get_post_info
from ..api.models import PostInfo
from ..bot import bot
from ..utils.url import get_lab_link


def get_help_article() -> InlineQueryResultArticle:
    text = f"欢迎使用 @{bot.me.username} 来转换 米游社/HoYoLab 链接，您也可以将 Bot 添加到群组或频道自动匹配消息。"
    return InlineQueryResultArticle(
        title=">> 帮助 <<",
        description="将 Bot 添加到群组或频道可以自动匹配消息。",
        input_message_content=InputTextMessageContent(text),
        reply_markup=get_test_button(),
    )


def get_article(message: str) -> Optional[InlineQueryResultArticle]:
    return InlineQueryResultArticle(
        title=">> 转换结果 <<",
        description="点击发送文本",
        input_message_content=InputTextMessageContent(
            message, disable_web_page_preview=False
        ),
    )


def get_notice(message: str) -> InlineQueryResultArticle:
    return InlineQueryResultArticle(
        title=">> 如果没有正确显示图片和原图，请稍后重试 <<",
        description="服务器请求中，请等待...",
        input_message_content=InputTextMessageContent(
            message, disable_web_page_preview=False
        ),
    )


async def add_document_results(
    message: str, post_info: PostInfo
) -> List[InlineQueryResult]:
    result = []
    text = f"<b>{post_info.subject}</b>\n\n{message}"[:1000]
    if post_info.image_urls:
        img = post_info.image_urls[0]
        result.append(
            InlineQueryResultPhoto(
                photo_url=img,
                title="图片",
                description="发送图片",
                caption=text,
            )
        )
        result.append(
            InlineQueryResultDocument(
                document_url=img,
                title="原图",
                description="发送原图",
                caption=text,
            )
        )
    return result


@bot.on_inline_query()
async def inline(_, query: InlineQuery):
    message = query.query
    results = [get_help_article()]
    if message:
        replace_list = get_lab_link(message)
        if replace_list:
            replaced_message = message
            for k, v in replace_list.items():
                replaced_message = message.replace(k, v)
            results.append(get_article(replaced_message))
            post_info = None
            try:
                post_info = await get_post_info(list(replace_list.values())[0])
            except Exception:
                pass
            if post_info:
                files = await add_document_results(message, post_info)
                if files:
                    results.append(get_notice(replaced_message))
                    results += files
    await query.answer(
        switch_pm_text="🔎 输入 米游社/HoYoLab 链接来转换",
        switch_pm_parameter="start",
        results=results,
    )
