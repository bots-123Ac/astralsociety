from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from keyboards.main_menu import leaderboard_kb, back_main_kb
from utils.database import get_global_leaderboard, get_user_rank
from utils.styler import fancy

router = Router()

MEDALS = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]


def _format_lb(rows, title):
    lines = [f"{title}\n━━━━━━━━━━━━━━━━━━━━━\n"]
    if not rows:
        lines.append("ησ ᴜsєʀs ʏєт.")
    else:
        for i, (name, uname, astral_id, coins) in enumerate(rows):
            display = f"@{uname}" if uname else (name or f"ID {astral_id}")
            lines.append(f"{MEDALS[i]} {display} — <b>{coins:,}</b> 🪙")
    return "\n".join(lines)


@router.message(F.text.regexp(r"^/aleaderboard(\s|$)"))
async def cmd_aleaderboard(message: Message):
    rows = await get_global_leaderboard(10)
    text = _format_lb(rows, "🌐 <b>ɢʟσвᴧʟ ʟєᴧᴅєʀвσᴧʀᴅ</b>")

    # Rank info
    rank = await get_user_rank(message.from_user.id)
    if rank:
        text += f"\n\n👤 ʏσᴜʀ ʀᴧηᴋ: <b>#{rank}</b>"

    if message.chat.type == "private":
        await message.answer(text, reply_markup=back_main_kb())
    else:
        await message.answer(text, reply_markup=leaderboard_kb())


@router.callback_query(F.data == "lb:group")
async def cb_group_lb(cb: CallbackQuery):
    # Group top 10 = all users (simplified — no per-group tracking implemented)
    rows = await get_global_leaderboard(10)
    text = _format_lb(rows, "👥 <b>ɢʀσᴜᴩ тσᴩ 10</b>")
    await cb.message.edit_text(text, reply_markup=leaderboard_kb())
    await cb.answer()
