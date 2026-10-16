"""
handlers/menu.py — /help, /about, and menu navigation.
Dynamic credits for main bot vs clone bot.
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery, LinkPreviewOptions,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import (
    CREATOR_1_NAME, CREATOR_1_ID,
    CREATOR_2_NAME, CREATOR_2_ID,
    MAIN_BOT_NAME, MAIN_BOT_USERNAME,
)
from keyboards.main_menu import main_menu_kb
from utils.bot_context import get_bot_context
from utils.database import (
    get_total_users, get_daily_active_users, get_quiz_count,
)

router = Router()


# ═══════════════════════════════════════════════
# /help
# ═══════════════════════════════════════════════
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


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        HELP_TEXT,
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )


# ═══════════════════════════════════════════════
# /about
# ═══════════════════════════════════════════════
def _about_text() -> str:
    ctx = get_bot_context()

    if ctx.get("is_clone", False):
        bot_name = ctx.get("bot_name") or "Clone Bot"
        bot_username = ctx.get("bot_username") or ""
        owner_name = ctx.get("owner_name") or "User"
        owner_username = ctx.get("owner_username") or ""

        if owner_username:
            owner_line = (
                f"<a href='https://t.me/{owner_username.lstrip('@')}'>"
                f"{owner_name}</a>"
            )
        else:
            owner_line = owner_name

        cloned_by = (
            f"<a href='https://t.me/{MAIN_BOT_USERNAME.lstrip('@')}'>"
            f"{MAIN_BOT_NAME}</a>"
        )

        owner_1 = f"<a href='tg://user?id={CREATOR_1_ID}'>{CREATOR_1_NAME}</a>"
        owner_2 = f"<a href='tg://user?id={CREATOR_2_ID}'>{CREATOR_2_NAME}</a>"

        return (
            f"ℹ️ <b>ᴀʙᴏᴜᴛ ᴛʜɪꜱ ʙᴏᴛ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🤖 ɴᴀᴍᴇ: <b>{bot_name}</b>\n"
            f"🆔 ᴜꜱᴇʀɴᴀᴍᴇ: @{bot_username}\n\n"
            f"👤 <b>ᴛʜɪꜱ ʙᴏᴛ ᴡᴀꜱ ᴍᴀᴅᴇ ʙʏ:</b>\n"
            f"{owner_line}\n\n"
            f"⚡ ᴘᴏᴡᴇʀᴇᴅ ʙʏ: {owner_line}\n"
            f"🤖 ᴄʟᴏɴᴇᴅ ʙʏ: {cloned_by}\n\n"
            f"👑 <b>ᴏʀɪɢɪɴᴀʟ ʙᴏᴛ ᴏᴡɴᴇʀꜱ:</b>\n"
            f"• {owner_1}\n"
            f"• {owner_2}"
        )

    # Main bot about
    return (
        "ℹ️ <b>ᴀʙᴏᴜᴛ ᴀꜱᴛʀᴀʟ ᴇᴍᴘɪʀᴇ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🤖 ɴᴀᴍᴇ: <b>{MAIN_BOT_NAME}</b>\n"
        f"🆔 ᴜꜱᴇʀɴᴀᴍᴇ: @{MAIN_BOT_USERNAME}\n\n"
        "ᴛʜᴇ ᴜʟᴛɪᴍᴀᴛᴇ ᴀʟʟ-ɪɴ-ᴏɴᴇ ᴛᴇʟᴇɢʀᴀᴍ ʙᴏᴛ\n"
        "ᴡɪᴛʜ ꜱᴛᴜᴅʏ, ɢᴀᴍᴇꜱ, ᴇᴄᴏɴᴏᴍʏ ᴀɴᴅ ᴍᴏʀᴇ.\n\n"
        "👑 <b>ᴏᴡɴᴇʀꜱ:</b>\n"
        f"• <a href='tg://user?id={CREATOR_1_ID}'>{CREATOR_1_NAME}</a>\n"
        f"• <a href='tg://user?id={CREATOR_2_ID}'>{CREATOR_2_NAME}</a>"
    )


@router.message(Command("about"))
async def cmd_about(message: Message):
    await message.answer(
        _about_text(),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )


# ═══════════════════════════════════════════════
# MENU CALLBACKS
# ═══════════════════════════════════════════════
@router.callback_query(F.data == "menu:main")
async def cb_menu_main(cb: CallbackQuery):
    name = cb.from_user.first_name or "User"
    title = get_bot_context().get("bot_name") or "˹𝐀𝐬𝐭𝐫𝐚𝐥 ꭙ 𝐄𝐦𝐩𝐢ʀᴇ˼"
    text = (
        f"🌌 <b>{title}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ʜᴇʏ <b>{name}</b>! 👋\n\n"
        f"🎯 ᴛᴀᴘ ᴀ ʙᴜᴛᴛᴏɴ ᴛᴏ ʙᴇɢɪɴ 👇"
    )
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
            _about_text(),
            reply_markup=kb.as_markup(),
            link_preview_options=LinkPreviewOptions(is_disabled=True),
        )
    except Exception:
        await cb.message.answer(_about_text())
    await cb.answer()
