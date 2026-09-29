import random
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
)

from utils.database import (
    get_or_create_user, add_coins, add_xp,
    get_treasure_plays, inc_treasure_play,
)
from utils.checks import dm_only

router = Router()

DAILY_LIMIT = 3
NORMAL_MIN = 500
NORMAL_MAX = 1000
SPECIAL_COINS = 15000
SPECIAL_XP = 100

ACTIVE_GAMES = {}


def boxes_kb(game_id: str, disabled: bool = False):
    rows = []
    for r in range(4):
        row = []
        for c in range(4):
            idx = r * 4 + c
            cb_data = f"treasure:{game_id}:{idx}" if not disabled else "treasure:noop"
            row.append(InlineKeyboardButton(text="🎁", callback_data=cb_data))
        rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.message(Command("treasure"))
@dm_only
async def cmd_treasure(message: Message):
    await get_or_create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
    )

    plays = await get_treasure_plays(message.from_user.id)

    if plays >= DAILY_LIMIT:
        return await message.reply(
            f"⏳ <b>ᴅᴀɪʟʏ ʟɪᴍɪᴛ ʀᴇᴀᴄʜᴇᴅ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"ʏᴏᴜ'ᴠᴇ ᴜꜱᴇᴅ <b>{plays}/{DAILY_LIMIT}</b> ᴛʀᴇᴀꜱᴜʀᴇ ʜᴜɴᴛꜱ ᴛᴏᴅᴀʏ.\n"
            f"ᴄᴏᴍᴇ ʙᴀᴄᴋ ᴛᴏᴍᴏʀʀᴏᴡ!"
        )

    game_id = f"{message.from_user.id}_{random.randint(1000, 9999)}"
    special_idx = random.randint(0, 15)

    boxes = {}
    for i in range(16):
        if i == special_idx:
            boxes[i] = {"coins": SPECIAL_COINS, "xp": SPECIAL_XP, "special": True}
        else:
            boxes[i] = {
                "coins": random.randint(NORMAL_MIN, NORMAL_MAX),
                "xp": 0, "special": False,
            }

    ACTIVE_GAMES[message.from_user.id] = {"game_id": game_id, "boxes": boxes}

    remaining = DAILY_LIMIT - plays - 1

    text = (
        f"💎 <b>ᴛʀᴇᴀꜱᴜʀᴇ ʜᴜɴᴛ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎁 ᴄʜᴏᴏꜱᴇ ᴀɴʏ ʙᴏx ꜰʀᴏᴍ ᴛʜᴇ 16 ʙᴇʟᴏᴡ!\n\n"
        f"🎯 ᴏɴᴇ ʙᴏx ʜᴀꜱ ᴀ <b>ᴊᴀᴄᴋᴘᴏᴛ</b>:\n"
        f"🪙 15,000 ᴄᴏɪɴꜱ + 📈 100 xᴘ\n\n"
        f"📅 ᴀᴛᴛᴇᴍᴘᴛꜱ ʟᴇꜰᴛ ᴀꜰᴛᴇʀ ᴛʜɪꜱ: <b>{remaining}/{DAILY_LIMIT}</b>"
    )
    await message.answer(text, reply_markup=boxes_kb(game_id))


@router.callback_query(F.data.startswith("treasure:"))
async def cb_treasure(cb: CallbackQuery):
    parts = cb.data.split(":")
    if len(parts) < 3 or parts[1] == "noop":
        return await cb.answer()

    game_id = parts[1]
    try:
        idx = int(parts[2])
    except ValueError:
        return await cb.answer()

    user_id = cb.from_user.id
    game = ACTIVE_GAMES.get(user_id)

    if not game or game["game_id"] != game_id:
        return await cb.answer("❌ ɢᴀᴍᴇ ᴇxᴘɪʀᴇᴅ. ᴜꜱᴇ /treasure ᴀɢᴀɪɴ.", show_alert=True)

    boxes = game["boxes"]
    reward = boxes.get(idx)
    if not reward:
        return await cb.answer("❌ ɪɴᴠᴀʟɪᴅ ʙᴏx.", show_alert=True)

    await add_coins(user_id, reward["coins"])
    if reward["xp"] > 0:
        await add_xp(user_id, reward["xp"])

    await inc_treasure_play(user_id)
    ACTIVE_GAMES.pop(user_id, None)

    if reward["special"]:
        result_text = (
            f"🎉🎉🎉 <b>ᴊᴀᴄᴋᴘᴏᴛ!</b> 🎉🎉🎉\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"ʏᴏᴜ ꜰᴏᴜɴᴅ ᴛʜᴇ <b>ꜱᴘᴇᴄɪᴀʟ ʙᴏx</b>! 🎁\n\n"
            f"🪙 +{SPECIAL_COINS:,} ᴄᴏɪɴꜱ\n"
            f"📈 +{SPECIAL_XP} xᴘ"
        )
    else:
        result_text = (
            f"🎁 <b>ᴛʀᴇᴀꜱᴜʀᴇ ᴏᴘᴇɴᴇᴅ!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🪙 +{reward['coins']:,} ᴄᴏɪɴꜱ"
        )

    try:
        await cb.message.edit_text(result_text)
    except Exception:
        await cb.message.answer(result_text)

    await cb.answer("🎉" if reward["special"] else "🎁")
