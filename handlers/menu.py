from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from config import (
    BOT_NAME,
    BOT_USERNAME,
    SUPPORT_GROUP_NAME,
    SUPPORT_GROUP_LINK,
    SUPPORT_CHANNEL_NAME,
    SUPPORT_CHANNEL_LINK,
    OWNER_ID,
)
from keyboards.main_menu import main_menu_kb, back_kb

router = Router()


# ─────────────────────────────────────────────
# 🏠 MAIN MENU (Back to Main)
# ─────────────────────────────────────────────
@router.callback_query(F.data == "menu:main")
async def back_to_main(callback: CallbackQuery):
    text = (
        f"👋 нi {callback.from_user.first_name}!\n\n"
        f"i'ϻ {BOT_NAME} — ʏσᴜʀ ᴧʟʟ-iη-σηє тєʟєɢʀᴧϻ "
        f"ᴄσϻᴩᴧηiση ғσʀ sᴛᴜᴅʏ, ɢʀσᴜᴩs, ɢᴧϻєs & ϻσʀє.\n\n"
        f"ᴄнσσsє ᴧη σᴩᴛiση вєʟσᴡ 👇"
    )
    await callback.message.edit_text(text, reply_markup=main_menu_kb())
    await callback.answer()


# ─────────────────────────────────────────────
# 🆘 HELP
# ─────────────────────────────────────────────
@router.callback_query(F.data == "menu:help")
async def show_help(callback: CallbackQuery):
    text = (
        f"🆘 {BOT_NAME} нєʟᴩ\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"• /start — sᴛᴧʀᴛ тнє вσᴛ\n"
        f"• /help — σᴩєη нєʟᴩ ϻєηᴜ\n"
        f"• /about — ᴧвσᴜᴛ тнє вσᴛ\n"
        f"• /profile — ᴠiєᴡ ʏσᴜʀ ᴩʀσғiʟє\n"
        f"• /stats — ᴠiєᴡ ʏσᴜʀ sᴛᴧᴛs\n"
        f"• /settings — вσᴛ sєᴛᴛiηɢs\n\n"
        f"ϻσʀє ᴄσϻϻᴧηᴅs ᴄσϻiηɢ sσση ✨"
    )
    await callback.message.edit_text(text, reply_markup=back_kb())
    await callback.answer()


# ─────────────────────────────────────────────
# ℹ️ ABOUT
# ─────────────────────────────────────────────
@router.callback_query(F.data == "menu:about")
async def show_about(callback: CallbackQuery):
    text = (
        f"ℹ️ ᴧвσᴜᴛ {BOT_NAME}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{BOT_NAME} is an all-in-one Telegram bot built for "
        f"students, communities and entertainment.\n\n"
        f"it ᴄσϻвiηєs sᴛᴜᴅʏ ʀєsσᴜʀᴄєs, ɢʀσᴜᴩ ϻᴧηᴧɢєϻєηᴛ, "
        f"ɢᴧϻєs, єᴄσησϻʏ, ǫᴜiᴢᴢєs, ᴜᴛiʟiᴛiєs ᴧηᴅ ϻσʀє iη σηє ᴩʟᴧᴄє.\n\n"
        f"🔗 ᴜsєʀηᴧϻє: {BOT_USERNAME}"
    )
    await callback.message.edit_text(text, reply_markup=back_kb())
    await callback.answer()


# ─────────────────────────────────────────────
# 👑 OWNER
# ─────────────────────────────────────────────
@router.callback_query(F.data == "menu:owner")
async def show_owner(callback: CallbackQuery):
    text = (
        f"👑 вσᴛ σᴡηєʀ\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ηᴧϻє: (ᴜᴩᴅᴧᴛє sσση)\n"
        f"ᴜsєʀηᴧϻє: (ᴜᴩᴅᴧᴛє sσση)\n"
        f"iᴅ: {OWNER_ID}\n\n"
        f"ᴩʀσғiʟє ʟiηᴋ вᴧᴧᴅ ϻє ᴧᴅᴅ нσ ʀнᴧ нᴧi."
    )
    await callback.message.edit_text(text, reply_markup=back_kb())
    await callback.answer()


# ─────────────────────────────────────────────
# 🥷 KIDNAP ME (Fun)
# ─────────────────────────────────────────────
@router.callback_query(F.data == "menu:kidnap")
async def kidnap_me(callback: CallbackQuery):
    text = (
        f"🥷 ᴋiᴅηᴧᴩ sᴜᴄᴄєssғᴜʟ!\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ʏσᴜ нᴧᴠє вєєη ᴋiᴅηᴧᴩᴩєᴅ вʏ {BOT_NAME} 👑\n\n"
        f"ʏσᴜ ᴧʀє ησω σғғiᴄiᴧʟʟʏ ᴩᴧʀᴛ σғ тнє "
        f"ᴧsᴛʀᴧʟ єϻᴩiʀє.\n\n"
        f"ησ єsᴄᴧᴩє. σηʟʏ sᴛᴜᴅʏ, ɢᴧϻєs & ғᴜη "
        f"ғʀσϻ ησω ση. 😈"
    )
    await callback.message.edit_text(text, reply_markup=back_kb())
    await callback.answer()
