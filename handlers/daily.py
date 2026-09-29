from aiogram import Router, F
from aiogram.types import Message

from config import (
    DAILY_NORMAL_COINS, DAILY_NORMAL_XP,
    DAILY_PREMIUM_COINS, DAILY_PREMIUM_XP,
)
from utils.database import (
    get_or_create_user, add_coins, add_xp, is_premium,
    can_claim_daily, mark_daily_claimed, get_pool,
)
from utils.checks import dm_only

router = Router()


@router.message(F.text.regexp(r"^/daily(@\w+)?(\s|$)"))
@dm_only
async def cmd_daily(message: Message):
    await get_or_create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
    )

    can, new_streak = await can_claim_daily(message.from_user.id)
    if not can:
        return await message.reply(
            f"⏳ ʏᴏᴜ'ᴠᴇ ᴀʟʀᴇᴀᴅʏ ᴄʟᴀɪᴍᴇᴅ ᴛᴏᴅᴀʏ!\n\n"
            f"ᴄᴏᴍᴇ ʙᴀᴄᴋ ᴛᴏᴍᴏʀʀᴏᴡ.\n"
            f"🔥 ꜱᴛʀᴇᴀᴋ: <b>{new_streak}</b>"
        )

    premium = await is_premium(message.from_user.id)
    coins = DAILY_PREMIUM_COINS if premium else DAILY_NORMAL_COINS
    xp = DAILY_PREMIUM_XP if premium else DAILY_NORMAL_XP

    await add_coins(message.from_user.id, coins)
    await add_xp(message.from_user.id, xp)
    await mark_daily_claimed(message.from_user.id, new_streak)

    header = "💎 ᴘʀᴇᴍɪᴜᴍ ᴅᴀɪʟʏ" if premium else "🎁 ᴅᴀɪʟʏ ʀᴇᴡᴀʀᴅ"
    await message.reply(
        f"<b>{header} ᴄʟᴀɪᴍᴇᴅ!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🪙 +{coins:,} ᴄᴏɪɴꜱ\n"
        f"📈 +{xp:,} xᴘ\n\n"
        f"🔥 ꜱᴛʀᴇᴀᴋ: <b>{new_streak}</b> ᴅᴀʏꜱ"
    )


@router.message(F.text.regexp(r"^/performance(@\w+)?(\s|$)"))
@dm_only
async def cmd_performance(message: Message):
    pool = await get_pool()
    row = await pool.fetchrow(
        """SELECT quiz_attempted, quiz_solved, word_attempted, word_solved,
                  number_attempted, number_guess
           FROM users WHERE user_id = $1""",
        message.from_user.id,
    )

    if not row:
        return await message.reply("❌ ʀᴇɢɪꜱᴛᴇʀ ꜰɪʀꜱᴛ ᴠɪᴀ /start.")

    qa = row["quiz_attempted"] or 0
    qs = row["quiz_solved"] or 0
    wa = row["word_attempted"] or 0
    ws = row["word_solved"] or 0
    na = row["number_attempted"] or 0
    ng = row["number_guess"] or 0

    total_att = qa + wa + na
    total_solved = qs + ws + ng
    accuracy = round((total_solved / total_att) * 100, 1) if total_att else 0.0

    await message.reply(
        f"📊 <b>ᴍʏ ᴘᴇʀꜰᴏʀᴍᴀɴᴄᴇ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🧠 ǫᴜɪᴢ ᴀᴛᴛᴇᴍᴘᴛᴇᴅ : <b>{qa}</b>\n"
        f"✅ ǫᴜɪᴢ ꜱᴏʟᴠᴇᴅ    : <b>{qs}</b>\n\n"
        f"🔢 ɴᴜᴍʙᴇʀ ᴀᴛᴛᴇᴍᴘᴛᴇᴅ: <b>{na}</b>\n"
        f"🎲 ɴᴜᴍʙᴇʀ ɢᴜᴇꜱꜱ   : <b>{ng}</b>\n\n"
        f"📈 ᴀᴄᴄᴜʀᴀᴄʏ     : <b>{accuracy}%</b>"
    )
