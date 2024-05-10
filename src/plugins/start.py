from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.bot import bot


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


@bot.on_message(filters=filters.command("start"))
async def start(_, message):
    await message.reply_text(
        HELP_MSG,
        quote=True,
        reply_markup=get_test_button(),
    )
