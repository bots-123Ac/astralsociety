"""
utils/welcome.py — Shared welcome/credits text builder.

Used by both `/start` handler and the `menu:main` callback so the
same exact message appears in both places.

Handles main bot vs clone bot dynamically.
"""

from config import (
    CREATOR_1_NAME, CREATOR_1_USERNAME, CREATOR_1_ID,
    CREATOR_2_NAME, CREATOR_2_USERNAME, CREATOR_2_ID,
    MAIN_BOT_NAME, MAIN_BOT_USERNAME,
)
from utils.bot_context import get_bot_context


# ═══════════════════════════════════════════════
# CREATOR LINKS
# ═══════════════════════════════════════════════
def _creators_links() -> str:
    """Clickable links to BOTH original creators."""
    u1 = CREATOR_1_USERNAME.lstrip("@")
    u2 = CREATOR_2_USERNAME.lstrip("@")
    return (
        f"<a href='https://t.me/{u1}'>{CREATOR_1_NAME}</a> & "
        f"<a href='https://t.me/{u2}'>{CREATOR_2_NAME}</a>"
    )


def _main_bot_link() -> str:
    """Clickable link to the original main bot."""
    u = MAIN_BOT_USERNAME.lstrip("@")
    return f"<a href='https://t.me/{u}'>{MAIN_BOT_NAME}</a>"


# ═══════════════════════════════════════════════
# WELCOME TEXT (shared by /start + menu:main)
# ═══════════════════════════════════════════════
def build_welcome_text(user_first_name: str) -> str:
    ctx = get_bot_context()

    # Bot display title
    if ctx.get("is_clone", False):
        display_title = ctx.get("bot_name") or "Clone Bot"
    else:
        display_title = MAIN_BOT_NAME

    return (
        f"🌌 <b>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ {display_title}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ʜᴇʏ <b>{user_first_name}</b>! 👋\n\n"
        f"ᴛʜɪꜱ ɪꜱ ᴀɴ ᴀʟʟ-ɪɴ-ᴏɴᴇ ᴛᴇʟᴇɢʀᴀᴍ ʙᴏᴛ ᴡɪᴛʜ:\n\n"
        f"📚 ꜱᴛᴜᴅʏ ᴍᴀᴛᴇʀɪᴀʟ\n"
        f"🎮 ɢᴀᴍᴇꜱ & ǫᴜɪᴢᴢᴇꜱ\n"
        f"💰 ᴇᴄᴏɴᴏᴍʏ ꜱʏꜱᴛᴇᴍ\n"
        f"⭐ xᴘ & ʟᴇᴠᴇʟꜱ\n"
        f"🏆 ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅꜱ\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ ᴘᴏᴡᴇʀᴇᴅ ʙʏ: {_creators_links()}\n"
        f"🤖 ᴄʟᴏɴᴇᴅ ʙʏ: {_main_bot_link()}\n\n"
        f"🎯 ᴛᴀᴘ ᴀ ʙᴜᴛᴛᴏɴ ᴛᴏ ʙᴇɢɪɴ 👇"
    )


# ═══════════════════════════════════════════════
# ABOUT TEXT
# ═══════════════════════════════════════════════
def build_about_text() -> str:
    ctx = get_bot_context()

    if ctx.get("is_clone", False):
        bot_name = ctx.get("bot_name") or "Clone Bot"
        bot_username = ctx.get("bot_username") or ""
        owner_name = ctx.get("owner_name") or "User"
        owner_username = ctx.get("owner_username") or ""
        owner_id = ctx.get("owner_id")

        # Owner clickable link (username preferred, else user id)
        if owner_username:
            owner_line = (
                f"<a href='https://t.me/{owner_username.lstrip('@')}'>"
                f"{owner_name}</a>"
            )
        elif owner_id:
            owner_line = f"<a href='tg://user?id={owner_id}'>{owner_name}</a>"
        else:
            owner_line = owner_name

        return (
            f"ℹ️ <b>ᴀʙᴏᴜᴛ ᴛʜɪꜱ ʙᴏᴛ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🤖 ɴᴀᴍᴇ: <b>{bot_name}</b>\n"
            f"🆔 ᴜꜱᴇʀɴᴀᴍᴇ: @{bot_username}\n\n"
            f"👤 <b>ᴛʜɪꜱ ʙᴏᴛ ᴡᴀꜱ ᴍᴀᴅᴇ ʙʏ:</b>\n"
            f"{owner_line}\n\n"
            f"🤖 ᴄʟᴏɴᴇᴅ ʙʏ: {_main_bot_link()}\n"
            f"⚡ ᴘᴏᴡᴇʀᴇᴅ ʙʏ: {_creators_links()}"
        )

    # Main bot about
    return (
        f"ℹ️ <b>ᴀʙᴏᴜᴛ ᴀꜱᴛʀᴀʟ ᴇᴍᴘɪʀᴇ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🤖 ɴᴀᴍᴇ: <b>{MAIN_BOT_NAME}</b>\n"
        f"🆔 ᴜꜱᴇʀɴᴀᴍᴇ: @{MAIN_BOT_USERNAME.lstrip('@')}\n\n"
        f"ᴛʜᴇ ᴜʟᴛɪᴍᴀᴛᴇ ᴀʟʟ-ɪɴ-ᴏɴᴇ ᴛᴇʟᴇɢʀᴀᴍ ʙᴏᴛ\n"
        f"ᴡɪᴛʜ ꜱᴛᴜᴅʏ, ɢᴀᴍᴇꜱ, ᴇᴄᴏɴᴏᴍʏ ᴀɴᴅ ᴍᴏʀᴇ.\n\n"
        f"⚡ ᴘᴏᴡᴇʀᴇᴅ ʙʏ: {_creators_links()}"
    )
