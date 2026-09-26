from aiogram import Router, F
from aiogram.types import CallbackQuery

from config import (
    BOT_NAME, BOT_USERNAME, SUPPORT_GROUP_NAME, SUPPORT_CHANNEL_NAME,
)
from keyboards.main_menu import main_menu_kb, back_kb
from keyboards.games_kb import game_lb_menu_kb
from utils.database import get_balance
from utils.ui import smart_edit

router = Router()


@router.callback_query(F.data == "menu:main")
async def back_to_main(cb: CallbackQuery):
    text = (
        f"👋 нi, <b>{cb.from_user.first_name}</b>!\n\n"
        f"ᴡєʟᴄσϻє тσ <b>{BOT_NAME}</b> 🌌\n\n"
        f"ᴄнσσsє ᴧη σᴩᴛiση вєʟσᴡ 👇"
    )
    await smart_edit(cb, text, main_menu_kb())
    await cb.answer()


@router.callback_query(F.data == "menu:help")
async def show_help(cb: CallbackQuery):
    text = (
        f"🆘 <b>{BOT_NAME} нєʟᴩ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"• /start — sᴛᴧʀᴛ вσᴛ\n"
        f"• /admin — ᴧᴅϻiη ᴩᴧηєʟ (ᴧᴅϻiηs σηʟʏ)\n"
        f"• /profile — ᴠiєᴡ ʏσᴜʀ ᴩʀσғiʟє\n"
        f"• /balance — ᴄнєᴄᴋ ᴄσiηs & ᴩσiηᴛs\n"
        f"• /leaderboard — ɢᴧϻє ʟєᴧᴅєʀвσᴧʀᴅ\n\n"
        f"ᴜsє iηʟiηє вᴜᴛᴛσηs ғσʀ ᴧʟʟ ғєᴧᴛᴜʀєs ✨"
    )
    await smart_edit(cb, text, back_kb())
    await cb.answer()


@router.callback_query(F.data == "menu:about")
async def show_about(cb: CallbackQuery):
    text = (
        f"ℹ️ <b>ᴧвσᴜᴛ {BOT_NAME}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{BOT_NAME} is an all-in-one Telegram bot built for students, "
        f"communities and entertainment.\n\n"
        f"it ᴄσϻвiηєs:\n"
        f"🎓 sᴛᴜᴅʏ ʀєsσᴜʀᴄєs\n"
        f"🛡️ ɢʀσᴜᴩ ϻᴧηᴧɢєϻєηᴛ\n"
        f"🎮 ɢᴧϻєs & єᴄσησϻʏ\n"
        f"🧠 ǫᴜiᴢᴢєs, ᴜᴛiʟiᴛiєs & ϻσʀє.\n\n"
        f"🔗 ᴜsєʀηᴧϻє: {BOT_USERNAME}"
    )
    await smart_edit(cb, text, back_kb())
    await cb.answer()


@router.callback_query(F.data == "menu:kidnap")
async def kidnap_me(cb: CallbackQuery):
    text = (
        f"🥷 <b>ᴋiᴅηᴧᴩ sᴜᴄᴄєssғᴜʟ!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ʏσᴜ нᴧᴠє вєєη ᴋiᴅηᴧᴩᴩєᴅ вʏ {BOT_NAME} 👑\n\n"
        f"ʏσᴜ ᴧʀє ησω σғғiᴄiᴧʟʟʏ ᴩᴧʀᴛ σғ "
        f"ᴧsᴛʀᴧʟ єϻᴩiʀє.\n\n"
        f"ησ єsᴄᴧᴩє. σηʟʏ sᴛᴜᴅʏ, ɢᴧϻєs & ғᴜη 😈"
    )
    await smart_edit(cb, text, back_kb())
    await cb.answer()


@router.callback_query(F.data == "menu:profile")
async def show_profile(cb: CallbackQuery):
    bal = await get_balance(cb.from_user.id)
    coins, points = (bal if bal else (0, 0))
    text = (
        f"👤 <b>ʏσᴜʀ ᴩʀσғiʟє</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ηᴧϻє: {cb.from_user.first_name}\n"
        f"ᴜsєʀηᴧϻє: @{cb.from_user.username or 'ησηє'}\n"
        f"iᴅ: <code>{cb.from_user.id}</code>\n\n"
        f"🪙 ᴄσiηs: <b>{coins}</b>\n"
        f"⭐ ᴩσiηᴛs: <b>{points}</b>"
    )
    await smart_edit(cb, text, back_kb())
    await cb.answer()


@router.callback_query(F.data == "menu:leaderboard")
async def show_lb_menu(cb: CallbackQuery):
    text = "🏆 <b>ɢᴧϻє ʟєᴧᴅєʀвσᴧʀᴅ</b>\n━━━━━━━━━━━━━━━━━━━━━\n\nᴄнσσsє ᴧ ɢᴧϻє:"
    await smart_edit(cb, text, game_lb_menu_kb())
    await cb.answer()
