from aiogram import Router, F
from aiogram.types import Message

from config import MISSION_REWARD_COINS, MISSION_REWARD_XP
from utils.database import (
    get_or_create_user, get_or_create_mission, mission_claim,
    add_coins, add_xp,
)

router = Router()


@router.message(F.text.regexp(r"^/mission(\s|$)"))
async def cmd_mission(message: Message):
    await get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    m = await get_or_create_mission(message.from_user.id)

    req = m["quizzes_required"]
    qdone = m["quiz_done"]
    pyq = m["pyq_downloaded"]
    claimed = m["claimed"]

    if claimed:
        return await message.reply(
            f"✅ ʏᴏᴜ'ᴠᴇ ᴀʟʀᴇᴀᴅʏ ᴄʟᴀɪᴍᴇᴅ ᴛᴏᴅᴀʏ'ꜱ ᴍɪꜱꜱɪᴏɴ!\nᴄᴏᴍᴇ ʙᴀᴄᴋ ᴛᴏᴍᴏʀʀᴏᴡ."
        )

    if req == 0:
        quiz_line = "1. 🧠 ꜱᴏʟᴠᴇ 0 ǫᴜɪᴢᴢᴇꜱ ✅ (ᴀᴜᴛᴏ-ᴅᴏɴᴇ)"
    else:
        mark = "✅" if qdone >= req else "⬜"
        quiz_line = f"1. 🧠 ꜱᴏʟᴠᴇ <b>{req}</b> ǫᴜɪᴢᴢᴇꜱ {mark} ({qdone}/{req})"

    pyq_line = f"2. 📚 ᴅᴏᴡɴʟᴏᴀᴅ ᴀ ᴘʏǫ (ᴄʟᴀꜱꜱ 10/11/12) {'✅' if pyq else '⬜'}"

    all_done = (qdone >= req) and pyq

    text = (
        f"🌟 <b>ᴅᴀɪʟʏ ᴀꜱᴛʀᴀʟ ᴍɪꜱꜱɪᴏɴ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{quiz_line}\n"
        f"{pyq_line}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎁 ʀᴇᴡᴀʀᴅ: <b>{MISSION_REWARD_COINS:,}</b> 🪙 + <b>{MISSION_REWARD_XP}</b> 📈"
    )

    if all_done:
        await add_coins(message.from_user.id, MISSION_REWARD_COINS)
        await add_xp(message.from_user.id, MISSION_REWARD_XP)
        await mission_claim(message.from_user.id)
        try:
            await message.bot.send_message(
                message.from_user.id,
                f"🌟 <b>ᴅᴀɪʟʏ ᴀꜱᴛʀᴀʟ ᴍɪꜱꜱɪᴏɴ ᴄᴏᴍᴘʟᴇᴛᴇᴅ!</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🪙 +{MISSION_REWARD_COINS:,} ᴄᴏɪɴꜱ\n"
                f"📈 +{MISSION_REWARD_XP} xᴘ\n\n"
                f"ᴄᴏᴍᴇ ʙᴀᴄᴋ ᴛᴏᴍᴏʀʀᴏᴡ!"
            )
        except Exception:
            pass
        text += "\n\n✅ <b>ᴍɪꜱꜱɪᴏɴ ᴄᴏᴍᴘʟᴇᴛᴇ!</b> ʀᴇᴡᴀʀᴅ ᴄʟᴀɪᴍᴇᴅ."

    await message.reply(text)
