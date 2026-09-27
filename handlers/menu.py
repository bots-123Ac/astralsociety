from aiogram import Router, F
from aiogram.types import CallbackQuery, Message

from config import BOT_NAME, BOT_USERNAME, CREDIT_HTML
from keyboards.main_menu import main_menu_kb, back_main_kb
from utils.ui import smart_edit

router = Router()


def help_text() -> str:
    return (
        f"🆘 <b>{BOT_NAME} — ʜᴇʟᴘ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>📚 ꜱᴛᴜᴅʏ</b>\n"
        f"/study — ʙʀᴏᴡꜱᴇ ꜱᴛᴜᴅʏ ᴍᴀᴛᴇʀɪᴀʟ (ᴅᴍ)\n\n"
        f"<b>🎮 ɢᴀᴍᴇꜱ</b>\n"
        f"/tgames — ǫᴜɪᴢ, ᴡᴏʀᴅ, ɴᴜᴍʙᴇʀ\n"
        f"/quiz — ꜱᴛᴀʀᴛ ᴀ ǫᴜɪᴢ\n"
        f"/new 5 — ꜱᴛᴀʀᴛ ᴡᴏʀᴅ ɢᴀᴍᴇ\n"
        f"/h 250 — ɢᴜᴇꜱꜱ ɪɴ ɴᴜᴍʙᴇʀ ɢᴀᴍᴇ\n\n"
        f"<b>🚀 ᴅᴀɪʟʏ</b>\n"
        f"/daily — ᴄʟᴀɪᴍ ᴅᴀɪʟʏ ʀᴇᴡᴀʀᴅ (ᴅᴍ)\n"
        f"/mission — ᴅᴀɪʟʏ ᴍɪꜱꜱɪᴏɴ\n\n"
        f"<b>🪙 ᴇᴄᴏɴᴏᴍʏ</b>\n"
        f"/profile — ᴠɪᴇᴡ ᴘʀᴏꜰɪʟᴇ\n"
        f"/convert 100c — ᴄᴏɪɴꜱ → ɢᴇᴍꜱ\n"
        f"/give 10000 — ꜱᴇɴᴅ ᴄᴏɪɴꜱ (ʀᴇᴘʟʏ)\n"
        f"/robs — ʀᴏʙ ᴜꜱᴇʀ (ʀᴇᴘʟʏ)\n"
        f"/shield 2 — ᴀᴄᴛɪᴠᴀᴛᴇ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ\n"
        f"/premium — ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ\n"
        f"/shop — ᴏᴘᴇɴ ꜱʜᴏᴘ (ᴅᴍ)\n"
        f"/powers — ᴀᴄᴛɪᴠᴇ ᴘᴏᴡᴇʀꜱ\n\n"
        f"<b>🏆 ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ</b>\n"
        f"/aleaderboard — ɢʟᴏʙᴀʟ ʀᴀɴᴋɪɴɢ\n"
        f"/performance — ʏᴏᴜʀ ꜱᴛᴀᴛꜱ (ᴅᴍ)\n\n"
        f"<b>👑 ᴀᴅᴍɪɴ</b>\n"
        f"/admin — ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ\n\n"
        f"🌠 ʟᴇᴀʀɴ • ᴘʟᴀʏ • ᴄᴏᴍᴘᴇᴛᴇ • ʀɪꜱᴇ"
    )


def about_text() -> str:
    return (
        f"ℹ️ <b>ᴀʙᴏᴜᴛ {BOT_NAME}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🤖 <b>ʙᴏᴛ ɴᴀᴍᴇ:</b> {BOT_NAME}\n"
        f"🔗 <b>ᴜꜱᴇʀɴᴀᴍᴇ:</b> {BOT_USERNAME}\n\n"
        f"<b>✨ ꜰᴇᴀᴛᴜʀᴇꜱ:</b>\n"
        f"📚 ꜱᴛᴜᴅʏ ᴍᴀᴛᴇʀɪᴀʟ ꜱʏꜱᴛᴇᴍ\n"
        f"📝 ǫᴜɪᴢ ꜱʏꜱᴛᴇᴍ\n"
        f"🎮 ᴛ-ɢᴀᴍᴇꜱ (ǫᴜɪᴢ, ᴡᴏʀᴅ, ɴᴜᴍʙᴇʀ)\n"
        f"🎯 ᴀᴜᴛᴏ ᴇᴠᴇɴᴛꜱ (ᴇᴠᴇʀʏ ʜᴏᴜʀ)\n"
        f"🪙 ᴄᴏɪɴꜱ & ɢᴇᴍꜱ ᴇᴄᴏɴᴏᴍʏ\n"
        f"🏆 ɢʟᴏʙᴀʟ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅꜱ\n"
        f"⭐ ᴘʀᴇᴍɪᴜᴍ ᴍᴇᴍʙᴇʀꜱʜɪᴘ\n"
        f"🛡️ ꜱʜɪᴇʟᴅ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ\n\n"
        f"⚠️ <b>ᴅɪꜱᴄʟᴀɪᴍᴇʀ:</b>\n"
        f"ᴀʟʟ ʀᴇᴡᴀʀᴅꜱ ᴀʀᴇ ᴠɪʀᴛᴜᴀʟ. ɴᴏ ʀᴇᴀʟ-ᴡᴏʀʟᴅ ᴠᴀʟᴜᴇ.\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"👨‍💻 <b>ᴘᴏᴡᴇʀᴇᴅ ʙʏ:</b>\n"
        f"{CREDIT_HTML}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🌠 ʟᴇᴀʀɴ • ᴘʟᴀʏ • ᴄᴏᴍᴘᴇᴛᴇ • ʀɪꜱᴇ"
    )


@router.callback_query(F.data == "menu:main")
async def back_main(cb: CallbackQuery):
    text = (
        f"👋 ʜɪ, <b>{cb.from_user.first_name}</b>!\n\n"
        f"ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ <b>{BOT_NAME}</b> 🌌\n\n"
        f"ʏᴏᴜʀ ᴀʟʟ-ɪɴ-ᴏɴᴇ ᴛᴇʟᴇɢʀᴀᴍ ᴄᴏᴍᴘᴀɴɪᴏɴ ғᴏʀ\n"
        f"ꜱᴛᴜᴅʏ, ɢᴀᴍᴇꜱ ᴀɴᴅ ᴍᴏʀᴇ.\n\n"
        f"ᴄʜᴏᴏꜱᴇ ᴀɴ ᴏᴘᴛɪᴏɴ ʙᴇʟᴏᴡ 👇\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"👨‍💻 {CREDIT_HTML}"
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


@router.message(F.text.regexp(r"^/help(\s|$)"))
async def cmd_help(message: Message):
    await message.answer(help_text(), reply_markup=back_main_kb())


@router.message(F.text.regexp(r"^/about(\s|$)"))
async def cmd_about(message: Message):
    await message.answer(about_text(), reply_markup=back_main_kb())
