import random
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
)

from utils.database import (
    get_or_create_user, add_coins, add_xp,
    get_luckydoor_plays, inc_luckydoor_play,
)

router = Router()

DAILY_LIMIT = 2          # 2 games per day
DOORS_PER_GAME = 4       # 4 doors per game
TOTAL_DOORS = 25

DOOR_NAMES = [
    "PRO", "RISKY", "SECRET", "HACKER", "MYSTERY",
    "SHADOW", "PHANTOM", "CHAOS", "LUCKY", "UNKNOWN",
    "DANGER", "FORTUNE", "LEGEND", "TRAP", "GHOST",
    "ELITE", "HIDDEN", "CURSED", "ROYAL", "VOID",
    "GOLDEN", "MASTER", "GOD MODE", "FINAL", "JACKPOT",
]

# Active games: (chat_id, user_id) -> game_dict
ACTIVE_GAMES = {}


# ═══════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════
def _generate_rewards():
    """
    25 doors:
      - 10 zero
      - 7 common  200-500
      - 5 medium  800-1600
      - 2 big     3000-5000
      - 1 jackpot 40000 + 400 XP
    """
    rewards = []
    for _ in range(10):
        rewards.append({"type": "zero", "coins": 0, "xp": 0})
    for _ in range(7):
        rewards.append({"type": "common", "coins": random.randint(200, 500), "xp": 0})
    for _ in range(5):
        rewards.append({"type": "medium", "coins": random.randint(800, 1600), "xp": 0})
    for _ in range(2):
        rewards.append({"type": "big", "coins": random.randint(3000, 5000), "xp": 0})
    rewards.append({"type": "jackpot", "coins": 40000, "xp": 400})
    random.shuffle(rewards)
    return rewards


def _opened_indexes(game):
    return {i for i, _ in game["opened"]}


def _icon_for(idx, game):
    for i, r in game["opened"]:
        if i == idx:
            return {
                "zero": "❌",
                "common": "🪙",
                "medium": "💰",
                "big": "💎",
                "jackpot": "👑",
            }.get(r["type"], "✅")
    return "🚪"


def doors_kb(game_id: str, game: dict):
    """Build 5x5 keyboard for 25 doors."""
    opened = _opened_indexes(game)
    rows = []
    for r in range(5):
        row = []
        for c in range(5):
            idx = r * 5 + c
            icon = _icon_for(idx, game)
            name = DOOR_NAMES[idx]
            if idx in opened:
                cb_data = "ld:noop"
            else:
                cb_data = f"ld:{game_id}:{idx}"
            row.append(InlineKeyboardButton(
                text=f"{icon} {name}",
                callback_data=cb_data
            ))
        rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _format_result(reward: dict) -> str:
    t = reward["type"]
    if t == "zero":
        return (
            "❌ <b>ʏᴏᴜ ɢᴏᴛ ᴢᴇʀᴏ ʀᴇᴡᴀʀᴅ ᴅᴏᴏʀ!</b>\n"
            "ʙᴇᴛᴛᴇʀ ʟᴜᴄᴋ ɴᴇxᴛ ᴛɪᴍᴇ.\n\n"
            "🪙 ʏᴏᴜ ɢᴏᴛ <b>0</b> ᴄᴏɪɴꜱ."
        )
    if t == "common":
        return (
            "🪙 <b>ʏᴏᴜ ɢᴏᴛ ᴀ ᴄᴏᴍᴍᴏɴ ʀᴇᴡᴀʀᴅ!</b>\n"
            "ʏᴏᴜ ᴄᴀɴ ɢᴇᴛ ᴛʜᴇ ᴊᴀᴄᴋᴘᴏᴛ! 🔥\n\n"
            f"🪙 ʏᴏᴜ ɢᴏᴛ <b>{reward['coins']:,}</b> ᴄᴏɪɴꜱ."
        )
    if t == "medium":
        return (
            "💰 <b>ʏᴏᴜ ɢᴏᴛ ᴀ ᴍᴇᴅɪᴜᴍ ʀᴇᴡᴀʀᴅ!</b>\n"
            "ʏᴏᴜ ᴄᴀɴ ɢᴇᴛ ᴛʜᴇ ᴊᴀᴄᴋᴘᴏᴛ! 🔥\n\n"
            f"🪙 ʏᴏᴜ ɢᴏᴛ <b>{reward['coins']:,}</b> ᴄᴏɪɴꜱ."
        )
    if t == "big":
        return (
            "💎 <b>ʏᴏᴜ ɢᴏᴛ ʙɪɢ ʀᴇᴡᴀʀᴅ!</b>\n"
            "ᴊᴜꜱᴛ ᴀ ꜱᴛᴇᴘ ᴛᴏ ᴊᴀᴄᴋᴘᴏᴛ! 🔥\n\n"
            f"🪙 ʏᴏᴜ ɢᴏᴛ <b>{reward['coins']:,}</b> ᴄᴏɪɴꜱ."
        )
    # jackpot
    return (
        "👑 <b>ᴄᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴꜱ!</b> 🎉\n\n"
        "ʏᴏᴜ ɢᴏᴛ ᴛʜᴇ <b>ʙɪɢɢᴇꜱᴛ ᴊᴀᴄᴋᴘᴏᴛ!</b> 👑🔥\n\n"
        f"🪙 ʏᴏᴜ ɢᴏᴛ <b>{reward['coins']:,}</b> ᴄᴏɪɴꜱ.\n"
        f"📈 ʏᴏᴜ ɢᴏᴛ <b>{reward['xp']}</b> xᴘ."
    )


def _intro_text(remaining_after: int) -> str:
    return (
        "🚪 <b>ᴄʜᴏᴏꜱᴇ ᴛʜᴇ ʟᴜᴄᴋʏ ᴅᴏᴏʀ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎯 25 ᴅᴏᴏʀꜱ — ᴏᴘᴇɴ ᴀɴʏ <b>4</b> ᴛᴏ ᴛʀʏ ʏᴏᴜʀ ʟᴜᴄᴋ!\n\n"
        "👑 1 ᴅᴏᴏʀ ʜᴀꜱ <b>ᴍᴀꜱꜱɪᴠᴇ ᴊᴀᴄᴋᴘᴏᴛ</b>:\n"
        "🪙 40,000 ᴄᴏɪɴꜱ + 📈 400 xᴘ\n\n"
        f"📅 ɢᴀᴍᴇꜱ ʟᴇꜰᴛ ᴀꜰᴛᴇʀ ᴛʜɪꜱ: <b>{remaining_after}/{DAILY_LIMIT}</b>\n\n"
        "🎁 ᴛᴀᴘ ᴀ ᴅᴏᴏʀ ᴛᴏ ᴏᴘᴇɴ ɪᴛ 👇"
    )


# ═══════════════════════════════════════════════
# /luckydoor — Works in DM + GC
# ═══════════════════════════════════════════════
@router.message(Command("luckydoor"))
async def cmd_luckydoor(message: Message):
    await get_or_create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
    )

    plays = await get_luckydoor_plays(message.from_user.id)
    if plays >= DAILY_LIMIT:
        return await message.reply(
            f"⏳ <b>ᴅᴀɪʟʏ ʟɪᴍɪᴛ ʀᴇᴀᴄʜᴇᴅ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"ʏᴏᴜ'ᴠᴇ ᴜꜱᴇᴅ <b>{plays}/{DAILY_LIMIT}</b> ɢᴀᴍᴇꜱ ᴛᴏᴅᴀʏ.\n"
            f"ᴄᴏᴍᴇ ʙᴀᴄᴋ ᴛᴏᴍᴏʀʀᴏᴡ!"
        )

    key = (message.chat.id, message.from_user.id)
    if key in ACTIVE_GAMES:
        return await message.reply(
            "⚠️ ʏᴏᴜ ᴀʟʀᴇᴀᴅʏ ʜᴀᴠᴇ ᴀɴ ᴀᴄᴛɪᴠᴇ ɢᴀᴍᴇ. ꜰɪɴɪꜱʜ ɪᴛ ꜰɪʀꜱᴛ!"
        )

    game_id = f"{message.from_user.id}_{random.randint(10000, 99999)}"
    rewards = _generate_rewards()

    ACTIVE_GAMES[key] = {
        "game_id": game_id,
        "rewards": rewards,
        "opened": [],
    }

    remaining_after = DAILY_LIMIT - plays - 1

    await message.answer(
        _intro_text(remaining_after),
        reply_markup=doors_kb(game_id, ACTIVE_GAMES[key])
    )


# ═══════════════════════════════════════════════
# Callback — Door Open
# ═══════════════════════════════════════════════
@router.callback_query(F.data.startswith("ld:"))
async def cb_luckydoor(cb: CallbackQuery):
    parts = cb.data.split(":")
    if len(parts) < 2 or parts[1] == "noop":
        return await cb.answer()

    game_id = parts[1]
    try:
        idx = int(parts[2])
    except (ValueError, IndexError):
        return await cb.answer()

    key = (cb.message.chat.id, cb.from_user.id)
    game = ACTIVE_GAMES.get(key)

    if not game or game["game_id"] != game_id:
        return await cb.answer("❌ ɢᴀᴍᴇ ᴇxᴘɪʀᴇᴅ. ᴜꜱᴇ /luckydoor ᴀɢᴀɪɴ.", show_alert=True)

    # Already opened?
    if any(i == idx for i, _ in game["opened"]):
        return await cb.answer("🔒 ᴅᴏᴏʀ ᴀʟʀᴇᴀᴅʏ ᴏᴘᴇɴᴇᴅ")

    # Max doors?
    if len(game["opened"]) >= DOORS_PER_GAME:
        return await cb.answer("ᴍᴀx ᴅᴏᴏʀꜱ ᴏᴘᴇɴᴇᴅ", show_alert=True)

    # Open door
    reward = game["rewards"][idx]
    game["opened"].append((idx, reward))

    # Apply reward
    if reward["coins"] > 0:
        await add_coins(cb.from_user.id, reward["coins"])
    if reward["xp"] > 0:
        await add_xp(cb.from_user.id, reward["xp"])

    # Show result message
    door_name = DOOR_NAMES[idx]
    result_text = f"🚪 <b>ᴅᴏᴏʀ: {door_name}</b>\n\n" + _format_result(reward)

    try:
        await cb.message.answer(result_text)
    except Exception:
        pass

    # If 4 doors opened → finalize
    if len(game["opened"]) >= DOORS_PER_GAME:
        await inc_luckydoor_play(cb.from_user.id)

        total_coins = sum(r["coins"] for _, r in game["opened"])
        total_xp = sum(r["xp"] for _, r in game["opened"])

        # Find jackpot index
        jackpot_idx = next(
            (i for i, r in enumerate(game["rewards"]) if r["type"] == "jackpot"),
            None,
        )
        jackpot_info = ""
        if jackpot_idx is not None:
            jackpot_info = (
                f"\n\n👑 ᴛʜᴇ ᴊᴀᴄᴋᴘᴏᴛ ᴡᴀꜱ ɪɴ ᴅᴏᴏʀ #{jackpot_idx + 1}: "
                f"<b>{DOOR_NAMES[jackpot_idx]}</b>"
            )

        summary = (
            f"🏁 <b>ɢᴀᴍᴇ ᴏᴠᴇʀ!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 ʏᴏᴜ ᴏᴘᴇɴᴇᴅ <b>{len(game['opened'])}</b> ᴅᴏᴏʀꜱ.\n\n"
            f"🪙 ᴛᴏᴛᴀʟ ᴄᴏɪɴꜱ: <b>{total_coins:,}</b>\n"
            f"📈 ᴛᴏᴛᴀʟ xᴘ: <b>{total_xp}</b>"
            f"{jackpot_info}"
        )

        try:
            await cb.message.answer(summary)
        except Exception:
            pass

        ACTIVE_GAMES.pop(key, None)

        # Remove keyboard
        try:
            await cb.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass

    else:
        # Update door grid with opened door marked
        try:
            await cb.message.edit_reply_markup(reply_markup=doors_kb(game_id, game))
        except Exception:
            pass

    await cb.answer()
