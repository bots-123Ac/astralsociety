import random
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
)

from utils.database import (
    get_or_create_user, add_coins, add_xp,
    get_bombdefuse_plays, inc_bombdefuse_play,
    try_play_game, format_level_up_message,
)

router = Router()

DAILY_LIMIT = 3
MAX_PICKS = 2

ACTIVE_GAMES = {}


def boxes_kb(game_id: str, game: dict):
    opened = {i for i, _ in game["opened"]}
    rows = []
    for r in range(3):
        row = []
        for c in range(4):
            idx = r * 4 + c
            if idx in opened:
                reward = next((r for i, r in game["opened"] if i == idx), None)
                icon = {
                    "bomb": "💣", "lucky": "🍀",
                    "treasure": "💰", "empty": "📦",
                }.get(reward.get("type", "empty") if reward else "empty", "✅")
            else:
                icon = "📦"
            cb_data = "bd:noop" if idx in opened else f"bd:{game_id}:{idx}"
            row.append(InlineKeyboardButton(text=icon, callback_data=cb_data))
        rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _generate_boxes():
    """Generate 12 boxes with rewards."""
    boxes = []
    # 1 bomb
    boxes.append({"type": "bomb", "coins": -10000, "xp": -100})
    # 1 lucky (big reward)
    boxes.append({"type": "lucky", "coins": 15000, "xp": 300})
    # 2 treasures
    for _ in range(2):
        boxes.append({"type": "treasure", "coins": random.randint(5000, 7000), "xp": 50})
    # 8 empties
    for _ in range(8):
        boxes.append({"type": "empty", "coins": 0, "xp": 0})
    random.shuffle(boxes)
    return boxes


def _intro_text(remaining_after: int) -> str:
    return (
        "💣 <b>ʙᴏᴍʙ ᴅᴇꜰᴜꜱᴇ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎯 12 ʙᴏxᴇꜱ ʜɪᴅᴅᴇɴ!\n"
        "ᴏᴘᴇɴ ᴜᴘ ᴛᴏ <b>2</b> ᴛᴏ ᴛʀʏ ʏᴏᴜʀ ʟᴜᴄᴋ.\n\n"
        "💣 ʙᴏᴍʙ: <b>-10,000 ᴄᴏɪɴꜱ</b>\n"
        "🍀 ʟᴜᴄᴋʏ: <b>+15,000 ᴄᴏɪɴꜱ</b>\n"
        "💰 ᴛʀᴇᴀꜱᴜʀᴇ: <b>+5,000 – 7,000</b>\n"
        "📦 ᴇᴍᴘᴛʏ: <b>0</b>\n\n"
        f"📅 ɢᴀᴍᴇꜱ ʟᴇꜰᴛ ᴀꜰᴛᴇʀ ᴛʜɪꜱ: <b>{remaining_after}/{DAILY_LIMIT}</b>\n\n"
        "ᴛᴀᴘ ᴀ ʙᴏx ᴛᴏ ᴏᴘᴇɴ ɪᴛ 👇"
    )


@router.message(Command("defuse"))
async def cmd_defuse(message: Message):
    await get_or_create_user(
        message.from_user.id, message.from_user.username, message.from_user.first_name
    )

    allowed, used_extra, plays_left = await try_play_game(
        message.from_user.id, get_bombdefuse_plays, DAILY_LIMIT
    )

    if not allowed:
        return await message.reply(
            f"⏳ <b>ᴅᴀɪʟʏ ʟɪᴍɪᴛ ʀᴇᴀᴄʜᴇᴅ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"ʏᴏᴜ'ᴠᴇ ᴜꜱᴇᴅ ᴀʟʟ <b>{DAILY_LIMIT}</b> ɢᴀᴍᴇꜱ.\n"
            f"ᴀɴᴅ ɴᴏ ᴇxᴛʀᴀ ᴘʟᴀʏꜱ ʀᴇᴍᴀɪɴɪɴɢ.\n\n"
            f"🎟️ ʙᴜʏ ᴇxᴛʀᴀ ᴘʟᴀʏ ꜰʀᴏᴍ /shop!"
        )

    key = (message.chat.id, message.from_user.id)
    if key in ACTIVE_GAMES:
        return await message.reply("⚠️ ʏᴏᴜ ᴀʟʀᴇᴀᴅʏ ʜᴀᴠᴇ ᴀɴ ᴀᴄᴛɪᴠᴇ ɢᴀᴍᴇ.")

    game_id = f"{message.from_user.id}_{random.randint(1000, 9999)}"
    boxes = _generate_boxes()

    ACTIVE_GAMES[key] = {"game_id": game_id, "boxes": boxes, "opened": []}

    plays = await get_bombdefuse_plays(message.from_user.id)
    remaining_after = max(0, DAILY_LIMIT - plays)

    header = "🎟️ <b>ᴇxᴛʀᴀ ᴘʟᴀʏ ᴜꜱᴇᴅ!</b>\n\n" if used_extra else ""

    await message.answer(
        header + _intro_text(remaining_after),
        reply_markup=boxes_kb(game_id, ACTIVE_GAMES[key])
    )


@router.callback_query(F.data.startswith("bd:"))
async def cb_defuse(cb: CallbackQuery):
    parts = cb.data.split(":")
    if len(parts) < 3 or parts[1] == "noop":
        return await cb.answer()

    game_id = parts[1]
    try:
        idx = int(parts[2])
    except ValueError:
        return await cb.answer()

    key = (cb.message.chat.id, cb.from_user.id)
    game = ACTIVE_GAMES.get(key)

    if not game or game["game_id"] != game_id:
        return await cb.answer("❌ ɢᴀᴍᴇ ᴇxᴘɪʀᴇᴅ.", show_alert=True)

    if any(i == idx for i, _ in game["opened"]):
        return await cb.answer("🔒 ʙᴏx ᴀʟʀᴇᴀᴅʏ ᴏᴘᴇɴᴇᴅ")

    if len(game["opened"]) >= MAX_PICKS:
        return await cb.answer("ᴍᴀx ʙᴏxᴇꜱ ᴏᴘᴇɴᴇᴅ", show_alert=True)

    reward = game["boxes"][idx]
    game["opened"].append((idx, reward))

    # ═══ Apply reward ═══
    xp_info = None
    if reward["coins"] > 0:
        await add_coins(cb.from_user.id, reward["coins"])
    elif reward["coins"] < 0:
        await add_coins(cb.from_user.id, reward["coins"], is_earning=False)

    if reward["xp"] > 0:
        xp_info = await add_xp(cb.from_user.id, reward["xp"])

    # ═══ Result message ═══
    rtype = reward["type"]
    if rtype == "bomb":
        text = (
            "💣 <b>ʙᴏᴍʙ!</b>\n\n"
            f"💥 ʏᴏᴜ ʟᴏꜱᴛ <b>{abs(reward['coins']):,}</b> ᴄᴏɪɴꜱ."
        )
    elif rtype == "lucky":
        text = (
            "🍀 <b>ʟᴜᴄᴋʏ!</b>\n\n"
            f"💰 ʏᴏᴜ ᴡᴏɴ <b>{reward['coins']:,}</b> ᴄᴏɪɴꜱ + 📈 {reward['xp']} xᴘ."
        )
    elif rtype == "treasure":
        text = (
            "💰 <b>ᴛʀᴇᴀꜱᴜʀᴇ!</b>\n\n"
            f"🪙 ʏᴏᴜ ᴡᴏɴ <b>{reward['coins']:,}</b> ᴄᴏɪɴꜱ."
        )
    else:
        text = "📦 <b>ᴇᴍᴘᴛʏ ʙᴏx.</b>\n\nʙᴇᴛᴛᴇʀ ʟᴜᴄᴋ ηєxᴛ."

    try:
        await cb.message.answer(text)
    except Exception:
        pass

    if xp_info:
        try:
            await cb.message.answer(format_level_up_message(xp_info))
        except Exception:
            pass

    # ═══ End game ═══
    if len(game["opened"]) >= MAX_PICKS:
        await inc_bombdefuse_play(cb.from_user.id)
        total_coins = sum(r["coins"] for _, r in game["opened"])
        total_xp = sum(r["xp"] for _, r in game["opened"] if r["xp"] > 0)

        summary = (
            f"🏁 <b>ɢᴀᴍᴇ ᴏᴠᴇʀ!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 ʙᴏxᴇꜱ ᴏᴘᴇɴᴇᴅ: <b>{len(game['opened'])}</b>\n\n"
            f"🪙 ɴᴇᴛ ᴄᴏɪɴꜱ: <b>{total_coins:+,}</b>\n"
            f"📈 ᴛᴏᴛᴀʟ xᴘ: <b>{total_xp}</b>"
        )
        try:
            await cb.message.answer(summary)
        except Exception:
            pass

        ACTIVE_GAMES.pop(key, None)
        try:
            await cb.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
    else:
        try:
            await cb.message.edit_reply_markup(reply_markup=boxes_kb(game_id, game))
        except Exception:
            pass

    await cb.answer()
