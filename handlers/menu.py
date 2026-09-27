from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from config import BOT_NAME, BOT_USERNAME
from keyboards.main_menu import main_menu_kb, back_kb
from utils.database import get_user_stats
from utils.ui import smart_edit

router = Router()


def leaderboard_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔤 ᴡᴏʀᴅ ɢᴀᴍᴇ", callback_data="lb:word")],
        [InlineKeyboardButton(text="📝 ǫᴜɪᴢ", callback_data="lb:quiz")],
        [InlineKeyboardButton(text="↩️ вᴀᴄᴋ", callback_data="menu:main")],
    ])


@router.callback_query(F.data == "menu:main")
async def back_main(cb: CallbackQuery):
    text = (
        f"👋 нi, <b>{cb.from_user.first_name}</b>!\n\n"
        f"ᴡєʟᴄσϻє тσ <b>{BOT_NAME}</b> 🌌\n\n"
        f"🎓 sᴛᴜᴅʏ  •  📝 ǫᴜiᴢ  •  🎮 ɢᴧϻєs\n"
        f"🏆 ʟєᴧᴅєʀвσᴧʀᴅ  •  👤 ᴩʀσғiʟє\n\n"
        f"ᴄнσσsє ᴧη σᴩᴛiση вєʟσᴡ 👇"
    )
    await smart_edit(cb, text, main_menu_kb())
    await cb.answer()


@router.callback_query(F.data == "menu:help")
async def help_menu(cb: CallbackQuery):
    text = (
        f"🆘 <b>{BOT_NAME} нєʟᴩ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"• /start — sᴛᴧʀᴛ вσᴛ\n"
        f"• /admin — ᴧᴅᴍɪɴ ᴩᴧηєʟ\n"
        f"• /quiz — sᴛᴧʀᴛ ǫᴜɪᴢ\n"
        f"• /new — ᴡᴏʀᴅ ɢᴜᴇssɪɴɢ ɢᴧᴍє\n"
        f"• /profile — ᴠɪᴇᴡ ʏᴏᴜʀ sᴛᴧᴛs\n"
        f"• /leaderboard — ɢᴧᴍє ʀᴧηᴋɪηɢ\n"
        f"• /settings — ɢʀᴏᴜᴩ sєᴛᴛɪηɢs\n\n"
        f"ᴜsє ɪηʟɪηє вᴜᴛᴛσηs ✨"
    )
    await smart_edit(cb, text, back_kb())
    await cb.answer()


@router.callback_query(F.data == "menu:about")
async def about_menu(cb: CallbackQuery):
    text = (
        f"ℹ️ <b>ᴧʙᴏᴜᴛ {BOT_NAME}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ᴀɴ ᴀʟʟ-ɪɴ-ᴏɴᴇ ᴛᴇʟᴇɢʀᴀᴍ ʙᴏᴛ ғᴏʀ:\n\n"
        f"🎓 sᴛᴜᴅʏ ᴍᴀᴛᴇʀɪᴀʟ\n"
        f"📝 ǫᴜɪᴢᴢᴇs\n"
        f"🎮 ɢᴀᴍᴇs\n"
        f"🛡️ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ\n"
        f"🏆 ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅs\n\n"
        f"🔗 ᴜsᴇʀηᴧᴍє: {BOT_USERNAME}"
    )
    await smart_edit(cb, text, back_kb())
    await cb.answer()


@router.callback_query(F.data == "menu:profile")
async def profile_menu(cb: CallbackQuery):
    s = await get_user_stats(cb.from_user.id)
    text = (
        f"👤 <b>ʏᴏᴜʀ ᴘʀᴏғɪʟᴇ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ηᴀᴍᴇ: {cb.from_user.first_name}\n"
        f"ᴜsᴇʀηᴀᴍᴇ: @{cb.from_user.username or 'ηᴏηᴇ'}\n"
        f"ɪᴅ: <code>{cb.from_user.id}</code>\n\n"
        f"🪙 ᴄᴏɪηs: <b>{s['coins']}</b>\n"
        f"⭐ ᴘᴏɪηᴛs: <b>{s['points']}</b>\n\n"
        f"📝 ǫᴜɪᴢ ᴀᴛᴛᴇᴍᴘᴛs: <b>{s['quiz_attempted']}</b>\n"
        f"✅ ᴄᴏʀʀᴇᴄᴛ: <b>{s['quiz_correct']}</b>\n"
        f"🔤 ᴡᴏʀᴅ ɢᴀᴍᴇs: <b>{s['word_games']}</b>\n"
        f"🏆 ᴡᴏʀᴅ sᴄᴏʀᴇ: <b>{s['word_score']}</b>"
    )
    await smart_edit(cb, text, back_kb())
    await cb.answer()


@router.callback_query(F.data == "menu:perf")
async def perf_menu(cb: CallbackQuery):
    from utils.database import get_quiz_stats
    total, correct, subjects = await get_quiz_stats(cb.from_user.id)
    acc = round((correct / total) * 100, 1) if total else 0
    lines = [f"📊 <b>ᴍʏ ᴘᴇʀғᴏʀᴍᴀηᴄᴇ</b>\n━━━━━━━━━━━━━━━━━━━━━\n"]
    lines.append(f"📝 ǫᴜɪᴢ ᴀᴛᴛᴇᴍᴘᴛs: <b>{total}</b>")
    lines.append(f"✅ ᴄᴏʀʀᴇᴄᴛ: <b>{correct}</b>")
    lines.append(f"🎯 ᴀᴄᴄᴜʀᴀᴄʏ: <b>{acc}%</b>\n")
    if subjects:
        lines.append("📚 <b>sᴜʙᴊᴇᴄᴛ-ᴡɪsᴇ:</b>")
        for sub, cnt, cor in subjects:
            if not sub:
                continue
            sacc = round((cor or 0) / cnt * 100, 1) if cnt else 0
            lines.append(f"  • {sub}: {cor or 0}/{cnt} ({sacc}%)")
    await smart_edit(cb, "\n".join(lines), back_kb())
    await cb.answer()


@router.callback_query(F.data == "menu:lb")
async def lb_menu(cb: CallbackQuery):
    text = "🏆 <b>ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ</b>\n━━━━━━━━━━━━━━━━━━━━━\n\nᴄʜᴏᴏsᴇ ᴄᴀᴛᴇɢᴏʀʏ:"
    await smart_edit(cb, text, leaderboard_menu_kb())
    await cb.answer()
