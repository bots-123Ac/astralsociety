"""
handlers/menu.py — /help, /about, and menu navigation.
Back button returns the SAME welcome text as /start.
About section contains all credits.
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery, LinkPreviewOptions,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.main_menu import main_menu_kb
from utils.welcome import build_welcome_text, build_about_text

router = Router()


HELP_TEXT = (
    "🆘 <b>ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅꜱ</b>\n"
    "━━━━━━━━━━━━━━━━━━━━━\n\n"
    "🏠 <b>ᴄᴏʀᴇ</b>\n"
    "/start /help /about\n\n"
    "👤 <b>ᴘʀᴏꜰɪʟᴇ</b>\n"
    "/balance /profile /convert 100c\n\n"
    "🪙 <b>ᴇᴄᴏɴᴏᴍʏ (ɢᴄ)</b>\n"
    "/gives 10000 /robs 5000\n"
    "/shield 2 /shieldcheck\n\n"
    "🎮 <b>ɢᴀᴍᴇꜱ</b>\n"
    "/treasure /luckydoor /defuse\n"
    "/tgames /quiz /h 250\n\n"
    "🚀 <b>ᴅᴀɪʟʏ</b>\n"
    "/daily /mission /performance\n\n"
    "⭐ <b>ᴘʀᴇᴍɪᴜᴍ & ꜱʜᴏᴘ</b>\n"
    "/premium /premiumstatus /setemoji\n"
    "/shop /powers\n\n"
    "🏆 <b>ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ</b>\n"
    "/aleaderboard\n\n"
    "🤖 <b>ᴄʟᴏɴᴇ</b>\n"
    "/clone /myclone /deleteclone\n\n"
    "📚 <b>ꜱᴛᴜᴅʏ</b>\n"
    "/study"
)


# ═══════════════════════════════════════════════
# /help
# ═══════════════════════════════════════════════
@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        HELP_TEXT,
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )


# ═══════════════════════════════════════════════
# /about
# ═══════════════════════════════════════════════
@router.message(Command("about"))
async def cmd_about(message: Message):
    await message.answer(
        build_about_text(),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )


# ═══════════════════════════════════════════════
# MENU CALLBACKS
# ═══════════════════════════════════════════════
@router.callback_query(F.data == "menu:main")
async def cb_menu_main(cb: CallbackQuery):
    text = build_welcome_text(cb.from_user.first_name or "User")
    try:
        await cb.message.edit_text(
            text,
            reply_markup=main_menu_kb(),
            link_preview_options=LinkPreviewOptions(is_disabled=True),
        )
    except Exception:
        await cb.message.answer(
            text,
            reply_markup=main_menu_kb(),
            link_preview_options=LinkPreviewOptions(is_disabled=True),
        )
    await cb.answer()


@router.callback_query(F.data == "menu:help")
async def cb_menu_help(cb: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="↩️ ʙᴀᴄᴋ", callback_data="menu:main")
    try:
        await cb.message.edit_text(
            HELP_TEXT,
            reply_markup=kb.as_markup(),
            link_preview_options=LinkPreviewOptions(is_disabled=True),
        )
    except Exception:
        await cb.message.answer(HELP_TEXT)
    await cb.answer()


@router.callback_query(F.data == "menu:about")
async def cb_menu_about(cb: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="↩️ ʙᴀᴄᴋ", callback_data="menu:main")
    try:
        await cb.message.edit_text(
            build_about_text(),
            reply_markup=kb.as_markup(),
            link_preview_options=LinkPreviewOptions(is_disabled=True),
        )
    except Exception:
        await cb.message.answer(build_about_text())
    await cb.answer()
