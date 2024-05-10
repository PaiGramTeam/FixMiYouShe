from typing import List

from pyrogram.types import InputTextMessageContent, InlineQueryResultArticle, InlineQuery

from ..bot import bot
from ..utils.url import get_lab_link


def get_help_article():
    text = f"欢迎使用 @{bot.me.username} 的 Inline 模式来转换链接，您也可以将 Bot 添加到群组或频道自动匹配消息。"
    return InlineQueryResultArticle(
        title=">> 帮助 <<",
        description="将 Bot 添加到群组或频道可以自动匹配消息。",
        input_message_content=InputTextMessageContent(text),
    )


def get_article(message: str) -> List[InlineQueryResultArticle]:
    if not message:
        return [get_help_article()]
    replace_list = get_lab_link(message)
    if not replace_list:
        return [get_help_article()]
    for k, v in replace_list.items():
        message = message.replace(k, v)
    return [
        get_help_article(),
        InlineQueryResultArticle(
            title=">> 转换结果 <<",
            description="点击发送",
            input_message_content=InputTextMessageContent(message, disable_web_page_preview=False),
        ),
    ]


@bot.on_inline_query()
async def inline(_, query: InlineQuery):
    message = query.query
    results = get_article(message)
    await query.answer(
        switch_pm_text="Hello!",
        switch_pm_parameter="start",
        results=results,
    )
