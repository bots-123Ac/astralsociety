from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, LinkPreviewOptions

from config import BOT_NAME, BOT_USERNAME, CREDIT_HTML
from keyboards.main_menu import main_menu_kb, back_main_kb

router = Router()

NO_PREVIEW = LinkPreviewOptions(is_disabled=True)


def help_text() -> str:
    return (
        f"🆘 <b>{BOT_NAME} — ʜᴇʟᴘ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>📚 ꜱᴛᴜᴅʏ</b>\n"
        f"/study — ʙʀᴏᴡꜱᴇ ꜱᴛᴜᴅʏ ᴍᴀᴛᴇʀɪᴀʟ (ᴅᴍ)\n\n"
        f"<b>🎮 ɢᴀᴍᴇꜱ (ᴅᴍ ᴏɴʟʏ)</b>\n"
        f"/tgames — ǫᴜɪᴢ (15 ᴄᴀᴛᴇɢᴏʀɪᴇꜱ) + ɴᴜᴍʙᴇʀ ɢᴀᴍᴇ\n"
        f"/quiz — ꜱᴛᴀʀᴛ ᴀ ǫᴜɪᴢ\n"
        f"/h 250 — ɢᴜᴇꜱꜱ ᴛʜᴇ ɴᴜᴍʙᴇʀ\n\n"
        f"<b>🚀 ᴅᴀɪʟʏ</b>\n"
        f"/daily — ᴄʟᴀɪᴍ ᴅᴀɪʟʏ ʀᴇᴡᴀʀᴅ (ᴅᴍ)\n"
        f"/mission — ᴅᴀɪʟʏ ᴍɪꜱꜱɪᴏɴ\n\n"
        f"<b>🪙 ᴇᴄᴏɴᴏᴍʏ</b>\n"
        f"/profile — ᴠɪᴇᴡ ᴘʀᴏꜰɪʟᴇ\n"
        f"/convert 100c — ᴄᴏɪɴꜱ → ɢᴇᴍꜱ\n"
        f"/gives 10000 — ꜱᴇɴᴅ ᴄᴏɪɴꜱ (ʀᴇᴘʟʏ)\n"
        f"/robs — ʀᴏʙ ᴀ ᴜꜱᴇʀ (ʀᴇᴘʟʏ)\n"
        f"/shield 2 — ᴀᴄᴛɪᴠᴀᴛᴇ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ\n"
        f"/shieldcheck — ᴄʜᴇᴄᴋ ꜱʜɪᴇʟᴅ\n"
        f"/shop — ᴏᴘᴇɴ ꜱʜᴏᴘ (ᴅᴍ)\n"
        f"/powers — ᴀᴄᴛɪᴠᴇ ᴘᴏᴡᴇʀꜱ\n\n"
        f"<b>⭐ ᴘʀᴇᴍɪᴜᴍ</b>\n"
        f"/premium — ᴘʀᴇᴍɪᴜᴍ ꜱʜᴏᴘ (ɢᴇᴍꜱ)\n"
        f"/premiumstatus — ᴄʜᴇᴄᴋ ꜱᴛᴀᴛᴜꜱ\n\n"
        f"<b>🏆 ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ</b>\n"
        f"/aleaderboard — ɢʟᴏʙᴀʟ ʀᴀɴᴋɪɴɢ\n"
        f"/performance — ʏᴏᴜʀ ꜱᴛᴀᴛꜱ (ᴅᴍ)\n\n"
        f"<b>👑 ᴀᴅᴍɪɴ</b>\n"
        f"/admin — ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ\n\n"
        f"🌠 ʟᴇᴀʀɴ • ᴘʟᴀʏ • ᴄᴏᴍᴘᴇᴛᴇ • ʀɪꜱᴇ"
    )


async def get_about_text() -> str:
    """Generate about text with live stats."""
    try:
        from utils.database import get_total_users, get_monthly_active_users
        total_users = await get_total_users()
        monthly_users = await get_monthly_active_users()
    except Exception:
        total_users = 0
        monthly_users = 0

    return (
        f"ℹ️ <b>ᴀʙᴏᴜᴛ {BOT_NAME}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🤖 <b>ʙᴏᴛ ɴᴀᴍᴇ:</b> {BOT_NAME}\n"
        f"🔗 <b>ᴜꜱᴇʀɴᴀᴍᴇ:</b> {BOT_USERNAME}\n\n"
        f"📊 <b>ʟɪᴠᴇ ꜱᴛᴀᴛꜱ:</b>\n"
        f"👥 ᴛᴏᴛᴀʟ ᴜꜱᴇʀꜱ   : <b>{total_users:,}</b>\n"
        f"📅 ᴍᴏɴᴛʜʟʏ ᴀᴄᴛɪᴠᴇ: <b>{monthly_users:,}</b>\n\n"
        f"<b>✨ ꜰᴇᴀᴛᴜʀᴇꜱ:</b>\n"
        f"📚 ꜱᴛᴜᴅʏ ᴍᴀᴛᴇʀɪᴀʟ\n"
        f"📝 ǫᴜɪᴢ (15 ᴄᴀᴛᴇɢᴏʀɪᴇꜱ)\n"
        f"🎮 ɴᴜᴍʙᴇʀ ɢᴀᴍᴇ (ᴅᴍ)\n"
        f"🪙 ᴄᴏɪɴꜱ & ɢᴇᴍꜱ ᴇᴄᴏɴᴏᴍʏ\n"
        f"🏆 ɢʟᴏʙᴀʟ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅꜱ\n"
        f"⭐ ᴘʀᴇᴍɪᴜᴍ (ᴠɪᴀ ɢᴇᴍꜱ)\n"
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
    try:
        await cb.message.edit_text(
            text,
            reply_markup=main_menu_kb(),
            link_preview_options=NO_PREVIEW,
        )
    except Exception:
        try:
            await cb.message.answer(
                text,
                reply_markup=main_menu_kb(),
                link_preview_options=NO_PREVIEW,
            )
        except Exception:
            pass
    await cb.answer()


@router.callback_query(F.data == "menu:help")
async def cb_help(cb: CallbackQuery):
    try:
        await cb.message.edit_text(
            help_text(),
            reply_markup=back_main_kb(),
            link_preview_options=NO_PREVIEW,
        )
    except Exception:
        try:
            await cb.message.answer(
                help_text(),
                reply_markup=back_main_kb(),
                link_preview_options=NO_PREVIEW,
            )
        except Exception:
            pass
    await cb.answer()


@router.callback_query(F.data == "menu:about")
async def cb_about(cb: CallbackQuery):
    text = await get_about_text()
    try:
        await cb.message.edit_text(
            text,
            reply_markup=back_main_kb(),
            link_preview_options=NO_PREVIEW,
        )
    except Exception:
        try:
            await cb.message.answer(
                text,
                reply_markup=back_main_kb(),
                link_preview_options=NO_PREVIEW,
            )
        except Exception:
            pass
    await cb.answer()


@router.message(F.text.regexp(r"^/help(\s|$)"))
async def cmd_help(message: Message):
    await message.answer(
        help_text(),
        reply_markup=back_main_kb(),
        link_preview_options=NO_PREVIEW,
    )


@router.message(F.text.regexp(r"^/about(\s|$)"))
async def cmd_about(message: Message):
    text = await get_about_text()
    await message.answer(
        text,
        reply_markup=back_main_kb(),
        link_preview_options=NO_PREVIEW,
    )
