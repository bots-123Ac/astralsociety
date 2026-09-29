from aiogram import Router, F
from aiogram.types import Message

from config import MISSION_REWARD_COINS, MISSION_REWARD_XP
from utils.database import (
    get_or_create_user, get_or_create_mission, mission_claim,
    add_coins, add_xp,
)

router = Router()


@router.message(F.text.regexp(r"^/mission(@\w+)?(\s|$)"))
async def cmd_mission(message: Message):
    await get_or_create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
    )
    m = await get_or_create_mission(message.from_user.id)

    req = m["quizzes_required"] or 0
    qdone = m["quiz_done"] or 0
    pyq = m["pyq_downloaded"] or 0
    claimed = m["claimed"] or 0

    if claimed:
        return await message.reply(
            f"✅ ʏᴏᴜ'ᴠᴇ ᴀʟʀᴇᴀᴅʏ ᴄʟᴀɪᴍᴇᴅ ᴛᴏᴅᴀʏ'ꜱ ᴍɪꜱꜱɪᴏɴ!\n"
            f"ᴄᴏᴍᴇ ʙᴀᴄᴋ ᴛᴏᴍᴏʀʀᴏᴡ."
        )

    # Quiz line
    if req == 0:
        quiz_line = "1. 🧠 ꜱᴏʟᴠᴇ 0 ǫᴜɪᴢᴢᴇꜱ ✅ (ᴀᴜᴛᴏ-ᴅᴏɴᴇ)"
        quiz_done_bool = True
    else:
        quiz_done_bool = qdone >= req
        mark = "✅" if quiz_done_bool else "⬜"
        quiz_line = f"1. 🧠 ꜱᴏʟᴠᴇ <b>{req}</b> ǫᴜɪᴢᴢᴇꜱ {mark} ({qdone}/{req})"

    # PYQ line
    pyq_done_bool = bool(pyq)
    pyq_line = f"2. 📚 ᴅᴏᴡɴʟᴏᴀᴅ ᴀ ᴘʏǫ (ᴄʟᴀꜱꜱ 10/11/12) {'✅' if pyq_done_bool else '⬜'}"

    all_done = quiz_done_bool and pyq_done_bool

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

        # Beautiful completion message (DM + reply)
        completion_text = (
            f"🌌 <b>ᴅᴀɪʟʏ ᴛᴀꜱᴋ ᴄᴏᴍᴘʟᴇᴛᴇᴅ!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🎉 ᴄᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴꜱ, <b>{message.from_user.first_name}</b>!\n\n"
            f"ʏᴏᴜ ʜᴀᴠᴇ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ᴛᴏᴅᴀʏ'ꜱ ᴅᴀɪʟʏ ᴛᴀꜱᴋ.\n\n"
            f"🪙 ʀᴇᴡᴀʀᴅ: <b>+{MISSION_REWARD_COINS:,} ᴀꜱᴛʀᴀʟ ᴄᴏɪɴꜱ</b>\n"
            f"📈 xᴘ: <b>+{MISSION_REWARD_XP} xᴘ</b>\n\n"
            f"🔥 ᴋᴇᴇᴘ ᴘʟᴀʏɪɴɢ, ᴋᴇᴇᴘ ᴄᴏᴍᴘᴇᴛɪɴɢ ᴀɴᴅ ᴋᴇᴇᴘ ʀɪꜱɪɴɢ!\n\n"
            f"ᴄᴏᴍᴇ ʙᴀᴄᴋ ᴛᴏᴍᴏʀʀᴏᴡ ꜰᴏʀ ᴀ ɴᴇᴡ ᴅᴀɪʟʏ ᴛᴀꜱᴋ. 🌠"
        )

        # Try DM
        try:
            await message.bot.send_message(message.from_user.id, completion_text)
        except Exception:
            pass

        # Also reply in current chat
        await message.reply(completion_text)
        return

    await message.reply(text)
