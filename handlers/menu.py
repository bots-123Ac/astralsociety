from aiogram import Router, F
from aiogram.types import CallbackQuery

from config import BOT_NAME, BOT_USERNAME
from keyboards.main_menu import main_menu_kb, back_main_kb
from utils.ui import smart_edit
from utils.styler import fancy

router = Router()


@router.callback_query(F.data == "menu:main")
async def back_main(cb: CallbackQuery):
    text = (
        f"👋 нi, <b>{cb.from_user.first_name}</b>!\n\n"
        f"ᴡєʟᴄσϻє ᴛσ <b>{BOT_NAME}</b> 🌌\n\n"
        f"ʏσᴜʀ ᴧʟʟ-iη-σηє ᴛєʟєɢʀᴧϻ ᴄσϻᴩᴧηiση ғσʀ "
        f"sᴛᴜᴅʏ, ɢᴧϻєs ᴧηᴅ ᴍσʀє.\n\n"
        f"ᴄнσσsє ᴧη σᴩᴛiση вєʟσᴡ 👇"
    )
    await smart_edit(cb, text, main_menu_kb())
    await cb.answer()


@router.callback_query(F.data == "menu:help")
async def menu_help(cb: CallbackQuery):
    text = (
        f"🆘 <b>{BOT_NAME} — нєʟᴩ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>📚 sᴛᴜᴅʏ</b>\n"
        f"/study — вʀσωsє sᴛᴜᴅʏ ϻᴧтєʀiᴧʟ (ᴅᴍ)\n\n"
        f"<b>🎮 ɢᴧϻєs</b>\n"
        f"/tgames — ǫᴜiᴢ, ᴡσʀᴅ, ηᴜϻвєʀ ɢᴧϻєs\n"
        f"/h — ɢᴜєss iη ηᴜϻвєʀ ɢᴧϻє\n\n"
        f"<b>🚀 ᴅᴧiʟʏ</b>\n"
        f"/daily — ᴄʟᴧiϻ ᴅᴧiʟʏ ᴄσiηs (ᴅᴍ)\n"
        f"/mission — ᴅᴧiʟʏ ᴍissiση\n\n"
        f"<b>🪙 єᴄσησϻʏ</b>\n"
        f"/convert 100ᴄ — ᴄσiηs → ɢєϻs\n"
        f"/robs — ʀσв ᴧ ᴜsєʀ (ʀєᴩʟʏ)\n"
        f"/shield 2 — ᴩʀσтєᴄтiση\n"
        f"/premium — ᴩʀєϻiᴜϻ ϻєϻвєʀsнiᴩ\n"
        f"/shop — sнσᴩ (ᴅᴍ)\n"
        f"/powers — ᴧᴄтiᴠє ᴩσᴡєʀs\n\n"
        f"<b>🏆 ʟєᴧᴅєʀвσᴧʀᴅ</b>\n"
        f"/aleaderboard — ɢʟσвᴧʟ ʟєᴧᴅєʀвσᴧʀᴅ\n\n"
        f"<b>👤 ᴩʀσғiʟє</b>\n"
        f"/profile — ʏσᴜʀ ᴩʀσғiʟє\n"
        f"/performance — ᴅєтᴧiʟєᴅ sтᴧтs (ᴅᴍ)\n\n"
        f"🌠 ʟєᴧʀη • ᴩʟᴧʏ • ᴄσϻᴩєтє • ʀisє"
    )
    await smart_edit(cb, text, back_main_kb())
    await cb.answer()


@router.callback_query(F.data == "menu:about")
async def menu_about(cb: CallbackQuery):
    text = (
        f"ℹ️ <b>ᴧвσᴜᴛ {BOT_NAME}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{BOT_NAME} is ᴧη ᴧʟʟ-iη-σηє ᴛєʟєɢʀᴧϻ вσᴛ ғσʀ "
        f"sᴛᴜᴅʏ, ɢᴧϻєs, єᴄσησϻʏ ᴧηᴅ ᴄσϻϻᴜηiтʏ.\n\n"
        f"🎓 sᴛᴜᴅʏ ʀєsσᴜʀᴄєs\n"
        f"🎮 ɢᴧϻєs & ǫᴜiᴢᴢєs\n"
        f"🪙 єᴄσησϻʏ (ᴄσiηs + ɢєϻs)\n"
        f"🏆 ʟєᴧᴅєʀвσᴧʀᴅs\n"
        f"⭐ ᴩʀєϻiᴜϻ ϻєϻвєʀsнiᴩ\n\n"
        f"⚠️ <b>ᴅisᴄʟᴧiϻєʀ</b>\n"
        f"ᴧʟʟ ʀєᴡᴧʀᴅs ᴧʀє ᴠiʀтᴜᴧʟ. ησ ʀєᴧʟ-ᴡσʀʟᴅ "
        f"ᴠᴧʟᴜє. σηʟʏ ғσʀ ɢᴧϻєᴩʟᴧʏ.\n\n"
        f"🔗 {BOT_USERNAME}"
    )
    await smart_edit(cb, text, back_main_kb())
    await cb.answer()
