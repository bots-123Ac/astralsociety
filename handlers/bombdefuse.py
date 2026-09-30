import random
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
)

from utils.database import (
    get_or_create_user, add_coins, add_xp,
    get_bombdefuse_plays, inc_bombdefuse_play, get_user_coins,
)

router = Router()

DAILY_LIMIT = 3
MAX_BOXES = 2

BOMB_PENALTY_COINS = 10000
BOMB_PENALTY_XP = 100
LUCKY_REWARD_COINS = 15000
LUCKY_REWARD_XP = 300

BOX_NAMES = [
    "Nova", "Vex", "Zed",
    "Luna", "Rex", "Aero",
    "Nyx", "Flux", "Kiro",
    "Echo", "Orion", "Volt",
]

# Active games: (chat_id, user_id) -> game_dict
ACTIVE_GAMES = {}


# ═══════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════
def _generate_boxes():
    """
    12 boxes:
      - 1 bomb
      - 2 lucky
      - 6 treasure (5000-7000 coins)
      - 3 empty
    """
    boxes = []
    boxes.append({"type": "bomb"})
    boxes.append({"type": "lucky"})
    boxes.append({"type": "lucky"})
    for _ in range(6):
        boxes.append({"type": "treasure", "coins": random.randint(5000, 7000)})
    for _ in range(3):
        boxes.append({"type": "empty"})
    random.shuffle(boxes)
    return boxes


def _opened_indexes(game):
    return {i for i, _ in game["opened"]}


def _icon_for(idx, game):
    for i, r in game["opened"]:
        if i == idx:
            return {
                "bomb": "💣",
                "lucky": "🍀",
                "treasure": "💰",
                "empty": "📦",
            }.get(r["type"], "✅")
    return "📦"


def boxes_kb(game_id: str, game: dict):
    """3 columns × 4 rows = 12 boxes."""
    opened = _opened_indexes(game)
    rows = []
    for r in range(4):
        row = []
        for c in range(3):
            idx = r * 3 + c
            icon = _icon_for(idx, game)
            name = BOX_NAMES[idx]
            cb_data = "bd:noop" if idx in opened else f"bd:{game_id}:{idx}"
            row.append(InlineKeyboardButton(
                text=f"{icon} {name}",
                callback_data=cb_data
            ))
        rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _intro_text(remaining_after: int, coins: int) -> str:
    return (
        "💣 <b>ʙᴏᴍʙ ᴅᴇꜰᴜꜱᴇ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎯 12 ʙᴏxᴇꜱ — ᴏᴘᴇɴ ᴜᴘ ᴛᴏ <b>2</b> ʙᴏxᴇꜱ!\n\n"
        "🔒 <b>ʜɪᴅᴅᴇɴ ᴄᴏɴᴛᴇɴᴛꜱ:</b>\n"
        "💣 1 ʙᴏᴍʙ | 🍀 2 ʟᴜᴄᴋʏ\n"
        "💰 6 ᴛʀᴇᴀꜱᴜʀᴇ | 📦 3 ᴇᴍᴘᴛʏ\n\n"
        "⚠️ <b>ɪꜰ ʙᴏᴍʙ:</b> -10,000 ᴄᴏɪɴꜱ, -100 xᴘ\n"
        "🍀 <b>ɪꜰ ʟᴜᴄᴋʏ:</b> +15,000 ᴄᴏɪɴꜱ, +300 xᴘ\n"
        "💰 <b>ɪꜰ ᴛʀᴇᴀꜱᴜʀᴇ:</b> +5,000–7,000 ᴄᴏɪɴꜱ\n\n"
        f"💰 ʏᴏᴜʀ ᴄᴏɪɴꜱ: <b>{coins:,}</b>\n"
        f"📅 ɢᴀᴍᴇꜱ ʟᴇꜰᴛ ᴀꜰᴛᴇʀ ᴛʜɪꜱ: <b>{remaining_after}/{DAILY_LIMIT}</b>\n\n"
        "🎁 ᴛᴀᴘ ᴀ ʙᴏx ᴛᴏ ᴏᴘᴇɴ ɪᴛ 👇"
    )


def _format_result(reward: dict) -> str:
    t = reward["type"]
    if t == "bomb":
        return (
            "💣 <b>ʏᴏᴜ ᴏᴘᴇɴᴇᴅ ʙᴏᴍʙ ʙᴏx!</b>\n\n"
            "ꜱᴏʀʀʏ, ʏᴏᴜ ʟᴏꜱᴛ <b>10,000</b> ᴄᴏɪɴꜱ ᴀɴᴅ <b>100</b> xᴘ."
        )
    if t == "lucky":
        return (
            "🍀 <b>ʏᴏᴜ ᴏᴘᴇɴᴇᴅ ʟᴜᴄᴋʏ ʙᴏx!</b>\n\n"
            "ʏᴏᴜ ʜᴀᴠᴇ ɢʀᴇᴀᴛ ʟᴜᴄᴋ!\n"
            "🪙 +15,000 ᴄᴏɪɴꜱ | 📈 +300 xᴘ"
        )
    if t == "treasure":
        return (
            "💰 <b>ʏᴏᴜ ᴏᴘᴇɴᴇᴅ ᴛʀᴇᴀꜱᴜʀᴇ ʙᴏx!</b>\n\n"
            f"🪙 ʏᴏᴜ ɢᴏᴛ <b>{reward['coins']:,}</b> ᴄᴏɪɴꜱ!"
        )
    # empty
    return (
        "📦 <b>ʏᴏᴜʀ ʙᴏx ᴡᴀꜱ ᴇᴍᴘᴛʏ.</b>\n\n"
        "ʙᴇᴛᴛᴇʀ ʟᴜᴄᴋ ɴᴇxᴛ ᴛɪᴍᴇ!"
    )


# ═══════════════════════════════════════════════
# /defuse — Works in DM + GC
# ═══════════════════════════════════════════════
@router.message(Command("defuse"))
async def cmd_defuse(message: Message):
    await get_or_create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
    )

    plays = await get_bombdefuse_plays(message.from_user.id)
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
    boxes = _generate_boxes()

    ACTIVE_GAMES[key] = {
        "game_id": game_id,
        "boxes": boxes,
        "opened": [],
    }

    coins = await get_user_coins(message.from_user.id)
    remaining_after = DAILY_LIMIT - plays - 1

    await message.answer(
        _intro_text(remaining_after, coins),
        reply_markup=boxes_kb(game_id, ACTIVE_GAMES[key])
    )


# ═══════════════════════════════════════════════
# Callback — Box Open
# ═══════════════════════════════════════════════
@router.callback_query(F.data.startswith("bd:"))
async def cb_defuse(cb: CallbackQuery):
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
        return await cb.answer("❌ ɢᴀᴍᴇ ᴇxᴘɪʀᴇᴅ. ᴜꜱᴇ /defuse ᴀɢᴀɪɴ.", show_alert=True)

    if any(i == idx for i, _ in game["opened"]):
        return await cb.answer("🔒 ʙᴏx ᴀʟʀᴇᴀᴅʏ ᴏᴘᴇɴᴇᴅ")

    if len(game["opened"]) >= MAX_BOXES:
        return await cb.answer("ᴍᴀx ʙᴏxᴇꜱ ᴏᴘᴇɴᴇᴅ", show_alert=True)

    reward = game["boxes"][idx]
    game["opened"].append((idx, reward))

    # ═══ Apply reward/penalty ═══
    if reward["type"] == "bomb":
        # Deduct coins (may go negative)
        await add_coins(cb.from_user.id, -BOMB_PENALTY_COINS, is_earning=False)
        # Deduct XP
        await add_xp(cb.from_user.id, -BOMB_PENALTY_XP)

    elif reward["type"] == "lucky":
        await add_coins(cb.from_user.id, LUCKY_REWARD_COINS)
        await add_xp(cb.from_user.id, LUCKY_REWARD_XP)

    elif reward["type"] == "treasure":
        await add_coins(cb.from_user.id, reward["coins"])

    # ═══ Send result message ═══
    box_name = BOX_NAMES[idx]
    result_text = f"📦 <b>ʙᴏx: {box_name}</b>\n\n" + _format_result(reward)

    try:
        await cb.message.answer(result_text)
    except Exception:
        pass

    # ═══ End conditions ═══
    bomb_hit = reward["type"] == "bomb"
    max_reached = len(game["opened"]) >= MAX_BOXES

    if bomb_hit or max_reached:
        # Log play
        await inc_bombdefuse_play(cb.from_user.id)

        # Summary
        total_coins = 0
        total_xp = 0
        for _, r in game["opened"]:
            if r["type"] == "bomb":
                total_coins -= BOMB_PENALTY_COINS
                total_xp -= BOMB_PENALTY_XP
            elif r["type"] == "lucky":
                total_coins += LUCKY_REWARD_COINS
                total_xp += LUCKY_REWARD_XP
            elif r["type"] == "treasure":
                total_coins += r["coins"]

        end_reason = "💣 ʙᴏᴍʙ!" if bomb_hit else "✅ 2 ʙᴏxᴇꜱ ᴏᴘᴇɴᴇᴅ"

        summary = (
            f"🏁 <b>ɢᴀᴍᴇ ᴏᴠᴇʀ!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 {end_reason}\n\n"
            f"🪙 ɴᴇᴛ ᴄᴏɪɴꜱ: <b>{'+' if total_coins >= 0 else ''}{total_coins:,}</b>\n"
            f"📈 ɴᴇᴛ xᴘ: <b>{'+' if total_xp >= 0 else ''}{total_xp}</b>"
        )

        try:
            await cb.message.answer(summary)
        except Exception:
            pass

        ACTIVE_GAMES.pop(key, None)

        # Disable keyboard
        try:
            await cb.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass

    else:
        # Update grid
        try:
            await cb.message.edit_reply_markup(reply_markup=boxes_kb(game_id, game))
        except Exception:
            pass

    await cb.answer()
