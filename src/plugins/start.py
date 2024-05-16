import contextlib
from datetime import datetime, timedelta

from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from src.bot import bot
from src.services.scheduler import scheduler

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


async def delete_message(message: Message):
    with contextlib.suppress(Exception):
        await message.delete()


def add_delete_message_task(message: Message):
    scheduler.add_job(
        delete_message,
        "date",
        run_date=datetime.now() + timedelta(seconds=60),
        args=(message,),
    )


@bot.on_message(filters=filters.command("start"))
async def start(_, message: "Message"):
    reply = await message.reply_text(
        HELP_MSG,
        quote=True,
        reply_markup=get_test_button(),
    )
    if message.chat and message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        add_delete_message_task(reply)
