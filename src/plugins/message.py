from pyrogram import filters
from pyrogram.enums import MessageEntityType
from pyrogram.errors import WebpageNotFound
from pyrogram.types import Message, MessageEntity

from src.bot import bot
from src.log import logger
from src.utils.url import get_lab_link


@bot.on_message(filters=filters.incoming, group=1)
async def process_link(_, message: Message):
    if not message.chat:
        return
    text = message.text or message.caption
    if not text:
        return
    markdown_text = text.markdown
    if not markdown_text:
        return
    links = get_lab_link(markdown_text)
    if not links:
        return
    link_text = list(links.values())
    logger.info("link_text %s", link_text)
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
            ) for idx, i in enumerate(link_text)
        ]
        await message.reply_text(
            text=text,
            quote=True,
            entities=entities,
        )
