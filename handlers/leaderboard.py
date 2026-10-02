from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from keyboards.main_menu import leaderboard_kb
from utils.database import get_leaderboard, get_user_leaderboard_rank

router = Router()

MEDALS = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

PERIOD_TITLES = {
    "today": "📅 <b>ᴛᴏᴅᴀʏ's ᴛᴏᴘ 10</b>",
    "weekly": "📆 <b>ᴡᴇᴇᴋʟʏ ᴛᴏᴘ 10</b>",
    "monthly": "🗓️ <b>ᴍᴏɴᴛʜʟʏ ᴛᴏᴘ 10</b>",
    "alltime": "🌐 <b>ᴀʟʟ-ᴛɪᴍᴇ ᴛᴏᴘ 10</b>",
}


def _format_lb(rows, period: str, rank) -> str:
    title = PERIOD_TITLES.get(period, "🏆 ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ")
    lines = [title, "━━━━━━━━━━━━━━━━━━━━━"]

    if not rows:
        lines.append("")
        lines.append("ηᴏ ᴇᴀʀɴɪηɢs ʏᴇᴛ.")
    else:
        lines.append("")
        for i, row in enumerate(rows):
            name = row["first_name"]
            uname = row["username"]
            astral_id = row["astral_id"]
            coins = row["coins"] or 0

            # ═══ Custom emoji (if set) ═══
            try:
                emoji = row["custom_emoji"] or ""
            except Exception:
                emoji = ""

            if emoji == "∅" or emoji == "none":
                emoji = ""

            prefix = f"{emoji} " if emoji else ""

            display = f"@{uname}" if uname else (name or f"ID {astral_id}")
            lines.append(f"{MEDALS[i]} {prefix}{display} — <b>{coins:,}</b> 🪙")

    lines.append("━━━━━━━━━━━━━━━━━━━━━")
    if rank:
        lines.append(f"👤 ʏᴏᴜʀ ʀᴀɴᴋ: <b>#{rank}</b>")
    else:
        lines.append("👤 ʏᴏᴜʀ ʀᴀɴᴋ: ηᴏᴛ ʀᴀɴᴋᴇᴅ ʏᴇᴛ")

    return "\n".join(lines)


async def _build_lb_text(period: str, user_id: int) -> str:
    rows = await get_leaderboard(period, 10)
    rank = await get_user_leaderboard_rank(user_id, period)
    return _format_lb(rows, period, rank)


@router.message(Command("aleaderboard"))
async def cmd_aleaderboard(message: Message):
    text = await _build_lb_text("alltime", message.from_user.id)
    await message.answer(text, reply_markup=leaderboard_kb())


@router.message(Command("leaderboard"))
async def cmd_leaderboard_alias(message: Message):
    await cmd_aleaderboard(message)


@router.callback_query(F.data.startswith("lb:"))
async def cb_lb_tab(cb: CallbackQuery):
    period = cb.data.split(":")[1]
    if period not in PERIOD_TITLES:
        return await cb.answer()

    text = await _build_lb_text(period, cb.from_user.id)

    try:
        await cb.message.edit_text(text, reply_markup=leaderboard_kb())
    except Exception:
        try:
            await cb.message.answer(text, reply_markup=leaderboard_kb())
        except Exception:
            pass

    await cb.answer(f"✅ {period.upper()}")
