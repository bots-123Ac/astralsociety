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
        f"/treasure — ᴛʀᴇᴀꜱᴜʀᴇ ʜᴜɴᴛ (ᴅᴍ)\n"
        f"/tgames — ǫᴜɪᴢ + ɴᴜᴍʙᴇʀ ɢᴀᴍᴇ (ᴅᴍ)\n"
        f"/quiz — ꜱᴛᴀʀᴛ ᴀ ǫᴜɪᴢ (ᴅᴍ)\n"
        f"/h 250 — ɢᴜᴇꜱꜱ ᴛʜᴇ ɴᴜᴍʙᴇʀ (ᴅᴍ)\n\n"
        f"<b>🚀 ᴅᴀɪʟʏ</b>\n"
        f"/daily — ᴄʟᴀɪᴍ ᴅᴀɪʟʏ ʀᴇᴡᴀʀᴅ (ᴅᴍ)\n"
        f"/mission — ᴅᴀɪʟʏ ᴍɪꜱꜱɪᴏɴ (ɢᴄ + ᴅᴍ)\n\n"
        f"<b>🪙 ᴇᴄᴏɴᴏᴍʏ (ɢᴄ + ᴅᴍ)</b>\n"
        f"/balance — ᴠɪᴇᴡ ʙᴀʟᴀɴᴄᴇ\n"
        f"/convert 100c — ᴄᴏɪɴꜱ → ɢᴇᴍꜱ\n"
        f"/gives 10000 — ꜱᴇɴᴅ ᴄᴏɪɴꜱ (ʀᴇᴘʟʏ, ɢᴄ)\n"
        f"/robs 5000 — ʀᴏʙ ᴀ ᴜꜱᴇʀ (ʀᴇᴘʟʏ, ɢᴄ)\n"
        f"/shield 2 — ᴀᴄᴛɪᴠᴀᴛᴇ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ\n"
        f"/shieldcheck — ᴄʜᴇᴄᴋ ꜱʜɪᴇʟᴅ\n"
        f"/powers — ᴀᴄᴛɪᴠᴇ ᴘᴏᴡᴇʀꜱ\n\n"
        f"<b>⭐ ᴘʀᴇᴍɪᴜᴍ</b>\n"
        f"/premium — ᴘʀᴇᴍɪᴜᴍ ꜱʜᴏᴘ (ɢᴇᴍꜱ)\n"
        f"/premiumstatus — ᴄʜᴇᴄᴋ ꜱᴛᴀᴛᴜꜱ\n\n"
        f"<b>🛒 ꜱʜᴏᴘ (ᴅᴍ)</b>\n"
        f"/shop — ᴏᴘᴇɴ ꜱʜᴏᴘ\n\n"
        f"<b>🏆 ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ</b>\n"
        f"/aleaderboard — ɢʟᴏʙᴀʟ ʀᴀɴᴋɪɴɢ\n"
        f"/performance — ʏᴏᴜʀ ꜱᴛᴀᴛꜱ (ᴅᴍ)\n\n"
        f"<b>👑 ᴀᴅᴍɪɴ</b>\n"
        f"/admin — ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ\n"
        f"/botstatus — ʙᴏᴛ ꜱᴛᴀᴛᴜꜱ\n"
        f"/users — ᴜꜱᴇʀ ꜱᴛᴀᴛꜱ\n\n"
        f"🌠 ʟᴇᴀʀɴ • ᴘʟᴀʏ • ᴄᴏᴍᴘᴇᴛᴇ • ʀɪꜱᴇ"
    )


async def get_about_text() -> str:
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
        f"🎮 ᴛʀᴇᴀꜱᴜʀᴇ + ɴᴜᴍʙᴇʀ ɢᴀᴍᴇ\n"
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
