from asyncio import sleep

from pyrogram import filters
from pyrogram.enums import MessageEntityType, ChatType
from pyrogram.errors import WebpageNotFound
from pyrogram.types import Message, MessageEntity

from src.bot import bot
from src.log import logger
from src.utils.url import get_lab_link

MAX_LINKS = 4


async def _need_chat(_, __, m: Message):
    return m.chat


async def _need_text(_, __, m: Message):
    return m.text or m.caption


async def _forward_from_bot(_, __, m: Message):
    return m.forward_from and m.forward_from.is_bot


async def _forward_in_group(_, __, m: Message):
    return (
        m.forward_date
        and m.chat
        and m.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]
        and not (
            m.sender_chat
            and m.forward_from_chat
            and m.sender_chat.id == m.forward_from_chat.id
        )
    )


need_chat = filters.create(_need_chat)
need_text = filters.create(_need_text)
forward_from_bot = filters.create(_forward_from_bot)
forward_in_group = filters.create(_forward_in_group)


async def process_single_link_func(message: Message, link_text: str):
    try:
        await message.reply_web_page(
            text="",
            quote=True,
            url=link_text,
        )
    except WebpageNotFound:
        text = "."
        entities = [
            MessageEntity(
                type=MessageEntityType.TEXT_LINK,
                offset=0,
                length=1,
                url=link_text,
            )
        ]
        await message.reply_text(
            text=text,
            quote=True,
            entities=entities,
        )


async def process_link_func(markdown_text: str, message: Message):
    links = get_lab_link(markdown_text)
    if not links:
        return
    link_text = list(links.values())
    logger.info("chat[%s] link_text %s", message.chat.id, link_text)
    if not link_text:
        return
    for link in link_text[:MAX_LINKS]:
        await process_single_link_func(message, link)
        await sleep(0.5)


@bot.on_message(
    filters=filters.incoming
    & ~filters.via_bot
    & need_text
    & need_chat
    & ~forward_from_bot
    & ~forward_in_group,
    group=1,
)
async def process_link(_, message: Message):
    text = message.text or message.caption
    markdown_text = text.markdown
    if not markdown_text:
        return
    if markdown_text.startswith("~"):
        return
    await process_link_func(markdown_text, message)


@bot.on_message(
    filters=filters.incoming
    & filters.command("parse")
    & ~filters.forwarded
    & ~filters.via_bot
    & need_chat,
)
async def parse_reply_link(_, message: Message):
    reply = message.reply_to_message
    if not reply:
        return
    text = reply.text or reply.caption
    if not text:
        return
    markdown_text = text.markdown
    if not markdown_text:
        return
    await process_link_func(markdown_text, reply)
