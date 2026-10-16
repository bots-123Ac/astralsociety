"""
handlers/start.py — /start + welcome + dynamic credits for main & clone bots.
"""

from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, LinkPreviewOptions

from keyboards.main_menu import main_menu_kb
from utils.database import get_or_create_user
from utils.bot_context import get_bot_context

router = Router()


# ═══════════════════════════════════════════════
# DYNAMIC CREDITS
# ═══════════════════════════════════════════════
def _credits_line() -> str:
    ctx = get_bot_context()

    if ctx.get("is_clone", False):
        owner_name = ctx.get("owner_name") or "User"
        owner_username = ctx.get("owner_username") or ""
        if owner_username:
            owner_link = f"<a href='https://t.me/{owner_username.lstrip('@')}'>{owner_name}</a>"
        else:
            owner_link = owner_name

        # Cloned by → main bot clickable
        from config import MAIN_BOT_NAME, MAIN_BOT_USERNAME
        cloned_by = (
            f"<a href='https://t.me/{MAIN_BOT_USERNAME.lstrip('@')}'>"
            f"{MAIN_BOT_NAME}</a>"
        )

        return (
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚡ ᴘᴏᴡᴇʀᴇᴅ ʙʏ: {owner_link}\n"
            f"🤖 ᴄʟᴏɴᴇᴅ ʙʏ: {cloned_by}"
        )

    # Main bot
    return (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "ᴘᴏᴡᴇʀᴇᴅ ʙʏ "
        "<a href='tg://user?id=7790607144'>⏤͟͞ 𝐂𝐑𝐀𝐙𝐘 𝐁𝐎𝐘 ᭄࿐</a> & "
        "<a href='tg://user?id=8165863254'>𝓚𝓪𝓷𝓷𝓪࿐✨🤟</a>"
    )


def _bot_title() -> str:
    ctx = get_bot_context()
    if ctx.get("is_clone", False):
        return ctx.get("bot_name") or "ᴄʟᴏɴᴇ ʙᴏᴛ"
    return "˹𝐀𝐬𝐭𝐫𝐚𝐥 ꭙ 𝐄𝐦𝐩𝐢𝐫𝐞˼"


# ═══════════════════════════════════════════════
# /start
# ═══════════════════════════════════════════════
@router.message(CommandStart())
async def cmd_start(message: Message):
    await get_or_create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
    )

    name = message.from_user.first_name or "User"
    title = _bot_title()

    text = (
        f"🌌 <b>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ {title}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ʜᴇʏ <b>{name}</b>! 👋\n\n"
        f"ᴛʜɪꜱ ɪꜱ ᴀɴ ᴀʟʟ-ɪɴ-ᴏɴᴇ ᴛᴇʟᴇɢʀᴀᴍ ʙᴏᴛ ᴡɪᴛʜ:\n\n"
        f"📚 ꜱᴛᴜᴅʏ ᴍᴀᴛᴇʀɪᴀʟ\n"
        f"🎮 ɢᴀᴍᴇꜱ & ǫᴜɪᴢᴢᴇꜱ\n"
        f"💰 ᴇᴄᴏɴᴏᴍʏ ꜱʏꜱᴛᴇᴍ\n"
        f"⭐ xᴘ & ʟᴇᴠᴇʟꜱ\n"
        f"🏆 ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅꜱ\n\n"
        f"{_credits_line()}\n\n"
        f"🎯 ᴛᴀᴘ ᴀ ʙᴜᴛᴛᴏɴ ᴛᴏ ʙᴇɢɪɴ 👇"
    )

    await message.answer(
        text,
        reply_markup=main_menu_kb(),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )
