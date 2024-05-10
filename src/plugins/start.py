from pyrogram import filters

from src.bot import bot


HELP_MSG = "此 BOT 将会自动回复可以转换成 Telegram 预览的 URL 链接，可以提供更直观、方便的浏览体验。"


@bot.on_message(filters=filters.command("start"))
async def start(_, message):
    await message.reply_text(HELP_MSG, quote=True)
