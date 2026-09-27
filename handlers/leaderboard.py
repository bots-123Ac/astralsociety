from aiogram import Router, F
from aiogram.types import CallbackQuery

from keyboards.game_kb import leaderboard_menu_kb
from keyboards.main_menu import back_kb
from utils.database import get_word_leaderboard, get_quiz_stats
from utils.ui import smart_edit

router = Router()


@router.callback_query(F.data == "lb:word")
async def lb_word(cb: CallbackQuery):
    rows = await get_word_leaderboard(10)
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    if not rows:
        body = "ηᴏ sᴄᴏʀᴇs ʏᴇᴛ."
    else:
        body = "\n".join(
            f"{medals[i]} {name} — <b>{score}</b>"
            for i, (name, uname, score) in enumerate(rows)
        )
    text = f"🏆 <b>ᴡᴏʀᴅ ɢᴀᴍᴇ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n{body}"
    await smart_edit(cb, text, leaderboard_menu_kb())
    await cb.answer()


@router.callback_query(F.data == "lb:quiz")
async def lb_quiz(cb: CallbackQuery):
    text = (
        f"🏆 <b>ǫᴜɪᴢ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ᴜsᴇ /profile ᴛᴏ sᴇᴇ ʏᴏᴜʀ ᴏᴡɴ sᴛᴀᴛs.\n"
        f"sᴜʙᴊᴇᴄᴛ-ᴡɪsᴇ ʀᴀɴᴋɪɴɢ ᴄᴏᴍɪɴɢ sᴏᴏɴ."
    )
    await smart_edit(cb, text, leaderboard_menu_kb())
    await cb.answer()
