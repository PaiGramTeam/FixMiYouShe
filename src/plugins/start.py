import contextlib
from asyncio import sleep

from persica.factory.component import BaseComponent
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from src.core.bot import TelegramBot

HELP_MSG = "此 BOT 将会自动回复可以转换成 Telegram 预览的 URL 链接，可以提供更直观、方便的浏览体验。"
TEST_URL = "https://m.miyoushe.com/ys?channel=xiaomi/#/article/51867765"


def get_test_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="🍰 尝试一下",
                    switch_inline_query=TEST_URL,
                ),
            ]
        ]
    )


async def start(_, message: "Message"):
    reply = await message.reply_text(
        HELP_MSG,
        quote=True,
        reply_markup=get_test_button(),
    )
    if message.chat and message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await sleep(30)
        with contextlib.suppress(Exception):
            await reply.delete()


class StartBotPlugin(BaseComponent):
    def __init__(self, telegram_bot: TelegramBot):
        @telegram_bot.bot.on_message(filters=filters.command("start"))
        async def _start(_, message: "Message"):
            await start(_, message)
