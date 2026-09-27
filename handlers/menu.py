from aiogram import Router, F
from aiogram.types import CallbackQuery, Message

from config import (
    BOT_NAME, BOT_USERNAME,
    CREATOR_1_NAME, CREATOR_1_USERNAME,
    CREATOR_2_NAME, CREATOR_2_USERNAME,
)
from keyboards.main_menu import main_menu_kb, back_main_kb
from utils.ui import smart_edit

router = Router()


# ═══════════════════════════════════════════════
# HELP TEXT
# ═══════════════════════════════════════════════
def help_text() -> str:
    return (
        f"🆘 <b>{BOT_NAME} — нєʟᴩ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>📚 sᴛᴜᴅʏ</b>\n"
        f"/study — ʙʀᴏᴡsᴇ sᴛᴜᴅʏ ᴍᴀᴛᴇʀɪᴀʟ (ᴅᴍ)\n\n"
        f"<b>🎮 ɢᴀᴍᴇs</b>\n"
        f"/tgames — ǫᴜɪᴢ, ᴡᴏʀᴅ, ɴᴜᴍʙᴇʀ\n"
        f"/quiz — sᴛᴀʀᴛ ᴀ ǫᴜɪᴢ\n"
        f"/new 5 — sᴛᴀʀᴛ ᴡᴏʀᴅ ɢᴀᴍᴇ\n"
        f"/h 250 — ɢᴜᴇss ɪɴ ɴᴜᴍʙᴇʀ ɢᴀᴍᴇ\n\n"
        f"<b>🚀 ᴅᴀɪʟʏ</b>\n"
        f"/daily — ᴄʟᴀɪᴍ ᴅᴀɪʟʏ ʀᴇᴡᴀʀᴅ (ᴅᴍ)\n"
        f"/mission — ᴅᴀɪʟʏ ᴍɪssɪᴏɴ\n\n"
        f"<b>🪙 ᴇᴄᴏɴᴏᴍʏ</b>\n"
        f"/profile — ᴠɪᴇᴡ ᴘʀᴏғɪʟᴇ\n"
        f"/convert 100c — ᴄᴏɪɴs → ɢᴇᴍs\n"
        f"/robs — ʀᴏʙ ᴜsᴇʀ (ʀᴇᴘʟʏ)\n"
        f"/shield 2 — ᴀᴄᴛɪᴠᴀᴛᴇ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ\n"
        f"/premium — ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ\n"
        f"/shop — ᴏᴘᴇɴ sʜᴏᴘ (ᴅᴍ)\n"
        f"/powers — ᴀᴄᴛɪᴠᴇ ᴘᴏᴡᴇʀs\n\n"
        f"<b>🏆 ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ</b>\n"
        f"/aleaderboard — ɢʟᴏʙᴀʟ ʀᴀɴᴋɪɴɢ\n"
        f"/performance — ʏᴏᴜʀ sᴛᴀᴛs (ᴅᴍ)\n\n"
        f"<b>🛡️ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b> <i>(ᴀᴅᴍɪɴ ᴏɴʟʏ)</i>\n"
        f"/mute /unmute — ᴍᴜᴛᴇ ᴜsᴇʀ\n"
        f"/ban /unban — ʙᴀɴ ᴜsᴇʀ\n"
        f"/kick — ᴋɪᴄᴋ ᴜsᴇʀ\n"
        f"/warn /unwarn — ᴡᴀʀɴ ᴜsᴇʀ\n"
        f"/lock /unlock — ʟᴏᴄᴋ ᴄᴏɴᴛᴇɴᴛ\n"
        f"/settings — ɢʀᴏᴜᴘ sᴇᴛᴛɪɴɢs\n"
        f"/purge — ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇs\n\n"
        f"<b>👑 ᴀᴅᴍɪɴ</b>\n"
        f"/admin — ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ\n\n"
        f"🌠 ʟᴇᴀʀɴ • ᴘʟᴀʏ • ᴄᴏᴍᴘᴇᴛᴇ • ʀɪsᴇ"
    )


# ═══════════════════════════════════════════════
# ABOUT TEXT — with credits
# ═══════════════════════════════════════════════
def about_text() -> str:
    return (
        f"ℹ️ <b>ᴀʙᴏᴜᴛ {BOT_NAME}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🤖 <b>ʙᴏᴛ ɴᴀᴍᴇ:</b> {BOT_NAME}\n"
        f"🔗 <b>ᴜsᴇʀɴᴀᴍᴇ:</b> {BOT_USERNAME}\n\n"
        f"<b>✨ ᴛʜɪs ʙᴏᴛ ɪɴᴄʟᴜᴅᴇs:</b>\n"
        f"📚 sᴛᴜᴅʏ ᴍᴀᴛᴇʀɪᴀʟ sʏsᴛᴇᴍ\n"
        f"📝 ǫᴜɪᴢ sʏsᴛᴇᴍ\n"
        f"🎮 ᴛ-ɢᴀᴍᴇs (ǫᴜɪᴢ, ᴡᴏʀᴅ, ɴᴜᴍʙᴇʀ)\n"
        f"🪙 ᴄᴏɪɴs & ɢᴇᴍs ᴇᴄᴏɴᴏᴍʏ\n"
        f"🏆 ɢʟᴏʙᴀʟ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅs\n"
        f"⭐ ᴘʀᴇᴍɪᴜᴍ ᴍᴇᴍʙᴇʀsʜɪᴘ\n"
        f"🛡️ sʜɪᴇʟᴅ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ\n\n"
        f"⚠️ <b>ᴅɪsᴄʟᴀɪᴍᴇʀ:</b>\n"
        f"ᴀʟʟ ʀᴇᴡᴀʀᴅs ᴀʀᴇ ᴠɪʀᴛᴜᴀʟ. ɴᴏ ʀᴇᴀʟ-ᴡᴏʀʟᴅ ᴠᴀʟᴜᴇ.\n"
        f"ᴏɴʟʏ ᴍᴇᴀɴᴛ ғᴏʀ ɢᴀᴍᴇᴘʟᴀʏ ᴀɴᴅ ᴇɴᴛᴇʀᴛᴀɪɴᴍᴇɴᴛ.\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"👨‍💻 <b>ᴘᴏᴡᴇʀᴇᴅ ʙʏ:</b>\n"
        f"• <b>{CREATOR_1_NAME}</b>\n"
        f"  {CREATOR_1_USERNAME}\n"
        f"• <b>{CREATOR_2_NAME}</b>\n"
        f"  {CREATOR_2_USERNAME}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🌠 ʟᴇᴀʀɴ • ᴘʟᴀʏ • ᴄᴏᴍᴘᴇᴛᴇ • ʀɪsᴇ"
    )


# ═══════════════════════════════════════════════
# CALLBACK HANDLERS
# ═══════════════════════════════════════════════
@router.callback_query(F.data == "menu:main")
async def back_main(cb: CallbackQuery):
    text = (
        f"👋 ʜɪ, <b>{cb.from_user.first_name}</b>!\n\n"
        f"ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ <b>{BOT_NAME}</b> 🌌\n\n"
        f"ʏᴏᴜʀ ᴀʟʟ-ɪɴ-ᴏɴᴇ ᴛᴇʟᴇɢʀᴀᴍ ᴄᴏᴍᴘᴀɴɪᴏɴ ғᴏʀ\n"
        f"ꜱᴛᴜᴅʏ, ɢᴀᴍᴇꜱ ᴀɴᴅ ᴍᴏʀᴇ.\n\n"
        f"ᴄʜᴏᴏꜱᴇ ᴀɴ ᴏᴘᴛɪᴏɴ ʙᴇʟᴏᴡ 👇"
    )
    await smart_edit(cb, text, main_menu_kb())
    await cb.answer()


@router.callback_query(F.data == "menu:help")
async def cb_help(cb: CallbackQuery):
    await smart_edit(cb, help_text(), back_main_kb())
    await cb.answer()


@router.callback_query(F.data == "menu:about")
async def cb_about(cb: CallbackQuery):
    await smart_edit(cb, about_text(), back_main_kb())
    await cb.answer()


# ═══════════════════════════════════════════════
# STANDALONE COMMANDS
# ═══════════════════════════════════════════════
@router.message(F.text.regexp(r"^/help(\s|$)"))
async def cmd_help(message: Message):
    await message.answer(help_text(), reply_markup=back_main_kb())


@router.message(F.text.regexp(r"^/about(\s|$)"))
async def cmd_about(message: Message):
    await message.answer(about_text(), reply_markup=back_main_kb())
