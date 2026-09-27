from datetime import datetime
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
    # m = (id, user_id, date, quizzes_required, quiz_done, word_played, pyq_downloaded, claimed)
    _, _, _, req, qdone, wplay, pyq, claimed = m

    if claimed:
        return await message.reply(
            f"✅ ʏσᴜ'ᴠє ᴀʟʀᴇᴀᴅʏ ᴄʟᴀɪᴍᴇᴅ ᴛᴏᴅᴀʏ's ᴍɪssɪᴏɴ!\n"
            f"ᴄᴏᴍᴇ ʙᴀᴄᴋ ᴛᴏᴍᴏʀʀᴏᴡ."
        )

    if req == 0:
        quiz_line = "1. 🧠 sσʟᴠє 0 ǫᴜiᴢᴢєs ✅ (ᴧᴜтσ-ᴅσηє)"
    else:
        mark = "✅" if qdone >= req else "⬜"
        quiz_line = f"1. 🧠 sσʟᴠє <b>{req}</b> ǫᴜiᴢᴢєs {mark}"

    word_line = f"2. 🔤 ᴩʟᴧʏ ᴡσʀᴅ ɢᴧϻє {'✅' if wplay else '⬜'}"
    pyq_line = f"3. 📚 ᴅσωηʟσᴧᴅ ᴧ ᴩʏǫ (ᴄʟᴧss 10 ᴏʀ 11) {'✅' if pyq else '⬜'}"

    all_done = (qdone >= req) and wplay and pyq

    text = (
        f"🌟 <b>ᴅᴧiʟʏ ᴧsᴛʀᴧʟ ϻissiση</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{quiz_line}\n"
        f"{word_line}\n"
        f"{pyq_line}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎁 ʀєᴡᴧʀᴅ: <b>{MISSION_REWARD_COINS:,}</b> 🪙 + <b>{MISSION_REWARD_XP}</b> 📈"
    )

    if all_done:
        await add_coins(message.from_user.id, MISSION_REWARD_COINS)
        await add_xp(message.from_user.id, MISSION_REWARD_XP)
        await mission_claim(message.from_user.id)

        # DM to user
        try:
            await message.bot.send_message(
                message.from_user.id,
                f"🌟 <b>ᴅᴧiʟʏ ᴧsᴛʀᴧʟ ϻissiση ᴄσϻᴩʟєᴛєᴅ!</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🪙 +{MISSION_REWARD_COINS:,} ᴄσiηs\n"
                f"📈 +{MISSION_REWARD_XP} xᴩ\n\n"
                f"ᴄσϻє вᴧᴄᴋ тσϻσʀʀσω тσ ᴄσϻᴩєтє ωiтн ʏσᴜʀ ғʀiєηᴅs!"
            )
        except Exception:
            pass

        text += "\n\n✅ <b>ᴍissiση ᴄσϻᴩʟєтє!</b> ʀєᴡᴧʀᴅ ᴄʟᴧiϻєᴅ."
        text += "\n\n🪙 +8000 | 📈 +200"

    await message.reply(text)
