from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from keyboards.main_menu import leaderboard_kb, back_main_kb
from utils.database import get_global_leaderboard, get_user_rank
from utils.ui import smart_edit

router = Router()

MEDALS = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]


def _format_lb(rows, title):
    lines = [f"{title}\n━━━━━━━━━━━━━━━━━━━━━\n"]
    if not rows:
        lines.append("ησ ᴜsєʀs ʏєᴛ.")
    else:
        for i, row in enumerate(rows):
            name = row["first_name"]
            uname = row["username"]
            astral_id = row["astral_id"]
            coins = row["coins"]
            display = f"@{uname}" if uname else (name or f"ID {astral_id}")
            lines.append(f"{MEDALS[i]} {display} — <b>{coins:,}</b> 🪙")
    return "\n".join(lines)


# ═══════════════════════════════════════════════
# /aleaderboard — DM + GC
# ═══════════════════════════════════════════════
@router.message(Command("aleaderboard"))
async def cmd_aleaderboard(message: Message):
    rows = await get_global_leaderboard(10)
    text = _format_lb(rows, "🌐 <b>ɢʟᴏʙᴀʟ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ</b>")

    rank = await get_user_rank(message.from_user.id)
    if rank:
        text += f"\n\n👤 ʏᴏᴜʀ ʀᴀɴᴋ: <b>#{rank}</b>"

    if message.chat.type == "private":
        await message.answer(text, reply_markup=back_main_kb())
    else:
        await message.answer(text, reply_markup=leaderboard_kb())


# ═══════════════════════════════════════════════
# ALIAS: /leaderboard → same as /aleaderboard
# ═══════════════════════════════════════════════
@router.message(Command("leaderboard"))
async def cmd_leaderboard_alias(message: Message):
    await cmd_aleaderboard(message)


# ═══════════════════════════════════════════════
# Group Top 10 button (only in GC)
# ═══════════════════════════════════════════════
@router.callback_query(F.data == "lb:group")
async def cb_group_lb(cb: CallbackQuery):
    rows = await get_global_leaderboard(10)
    text = _format_lb(rows, "👥 <b>ɢʀᴏᴜᴘ ᴛᴏᴘ 10</b>")
    await smart_edit(cb, text, leaderboard_kb())
    await cb.answer()
