from aiogram import Router, F
from aiogram.types import CallbackQuery

from config import BOT_NAME, BOT_USERNAME
from keyboards.main_menu import main_menu_kb, back_kb
from keyboards.game_kb import leaderboard_menu_kb
from utils.database import get_user_stats
from utils.ui import smart_edit

router = Router()


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
        f"<b>📚 sᴛᴜᴅʏ</b>\n"
        f"• вʀσωsє ησᴛєs, ᴅᴩᴩ, вσσᴋs\n\n"
        f"<b>📝 ǫᴜiᴢ</b>\n"
        f"• /quiz — sᴛᴧʀᴛ ǫᴜiᴢ\n"
        f"• ᴧᴛᴛєϻᴩᴛ ᴍᴄǫs ᴧηᴅ єᴧʀη ᴩσiηᴛs\n\n"
        f"<b>🎮 ɢᴧϻєs</b>\n"
        f"• /new — sᴛᴧʀᴛ ᴡσʀᴅ ɢᴜєssiηɢ ɢᴧϻє\n"
        f"• ᴛʏᴩє ɢᴜєssєs ɪɴ ᴄнᴧᴛ\n\n"
        f"<b>🏆 ʟєᴧᴅєʀвσᴧʀᴅ</b>\n"
        f"• /leaderboard — ᴛσᴩ ᴩʟᴧʏєʀs\n\n"
        f"<b>👑 ᴀᴅᴍɪɴ</b>\n"
        f"• /admin — ᴧᴅᴍɪɴ ᴩᴧηєʟ\n"
        f"• /warn /mute /kick /ban\n\n"
        f"ᴜsє ɪηʟɪηє вᴜᴛᴛσηs ✨"
    )
    await smart_edit(cb, text, back_kb())
    await cb.answer()


@router.callback_query(F.data == "menu:about")
async def about_menu(cb: CallbackQuery):
    text = (
        f"ℹ️ <b>ᴧвσᴜᴛ {BOT_NAME}</b>\n"
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
        f"👤 <b>ʏσᴜʀ ᴩʀσғiʟє</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ηᴧᴍє: {cb.from_user.first_name}\n"
        f"ᴜsᴇʀηᴧᴍє: @{cb.from_user.username or 'ησηє'}\n"
        f"ɪᴅ: <code>{cb.from_user.id}</code>\n\n"
        f"🪙 ᴄᴏɪɴs: <b>{s['coins']}</b>\n"
        f"⭐ ᴩᴏɪηᴛs: <b>{s['points']}</b>\n\n"
        f"📝 ǫᴜɪᴢ ᴀᴛᴛᴇᴍᴩᴛs: <b>{s['quiz_attempted']}</b>\n"
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

    lines = [f"📊 <b>ϻʏ ᴩєʀғσʀϻᴧηᴄє</b>\n━━━━━━━━━━━━━━━━━━━━━\n"]
    lines.append(f"📝 ǫᴜɪᴢ ᴀᴛᴛᴇᴍᴩᴛs: <b>{total}</b>")
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
    text = "🏆 <b>ʟєᴧᴅєʀвσᴧʀᴅ</b>\n━━━━━━━━━━━━━━━━━━━━━\n\nᴄнσσsє ᴄᴧᴛєɢσʀʏ:"
    await smart_edit(cb, text, leaderboard_menu_kb())
    await cb.answer()
