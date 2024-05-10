from pyrogram import filters
from pyrogram.enums import MessageEntityType
from pyrogram.errors import WebpageNotFound
from pyrogram.types import Message, MessageEntity

from src.bot import bot
from src.log import logger
from src.utils.url import get_lab_link


async def _need_chat(_, __, m: Message):
    return m.chat


async def _need_text(_, __, m: Message):
    return m.text or m.caption


async def _forward_from_bot(_, __, m: Message):
    return m.forward_from and m.forward_from.is_bot


need_chat = filters.create(_need_chat)
need_text = filters.create(_need_text)
forward_from_bot = filters.create(_forward_from_bot)


@bot.on_message(
    filters=filters.incoming
    & ~filters.via_bot
    & need_text
    & need_chat
    & ~forward_from_bot,
    group=1,
)
async def process_link(_, message: Message):
    text = message.text or message.caption
    markdown_text = text.markdown
    if not markdown_text:
        return
    if markdown_text.startswith("~"):
        return
    links = get_lab_link(markdown_text)
    if not links:
        return
    link_text = list(links.values())
    logger.info("chat[%s] link_text %s", message.chat.id, link_text)
    if not link_text:
        return
    try:
        await message.reply_web_page(
            text="",
            quote=True,
            url=link_text[0],
        )
    except WebpageNotFound:
        text = "." * len(link_text)
        entities = [
            MessageEntity(
                type=MessageEntityType.TEXT_LINK,
                offset=idx,
                length=idx + 1,
                url=i,
            )
            for idx, i in enumerate(link_text)
        ]
        await message.reply_text(
            text=text,
            quote=True,
            entities=entities,
        )
