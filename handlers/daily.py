from aiogram import Router, F
from aiogram.types import Message

from config import (
    DAILY_NORMAL_COINS, DAILY_NORMAL_XP,
    DAILY_PREMIUM_COINS, DAILY_PREMIUM_XP,
)
from utils.database import (
    get_or_create_user, add_coins, add_xp, is_premium,
    can_claim_daily, mark_daily_claimed,
)

router = Router()


@router.message(F.text.regexp(r"^/daily(\s|$)"))
async def cmd_daily(message: Message):
    if message.chat.type != "private":
        return await message.reply("📩 ᴜsє ᴛнis iη вσᴛ ᴅᴍ σηʟʏ.")

    await get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.first_name)

    can, new_streak = await can_claim_daily(message.from_user.id)
    if not can:
        return await message.reply(
            f"⏳ ʏσᴜ'ᴠє ᴧʟʀєᴧᴅʏ ᴄʟᴧiϻєᴅ ᴛσᴅᴧʏ!\n\n"
            f"ᴄσϻє вᴧᴄᴋ тσϻσʀʀσω.\n"
            f"🔥 sᴛʀєᴧᴋ: <b>{new_streak}</b>"
        )

    premium = await is_premium(message.from_user.id)
    coins = DAILY_PREMIUM_COINS if premium else DAILY_NORMAL_COINS
    xp = DAILY_PREMIUM_XP if premium else DAILY_NORMAL_XP

    await add_coins(message.from_user.id, coins)
    await add_xp(message.from_user.id, xp)
    await mark_daily_claimed(message.from_user.id, new_streak)

    header = "💎 ᴩʀєϻiᴜϻ ᴅᴧiʟʏ" if premium else "🎁 ᴅᴧiʟʏ ʀєωᴧʀᴅ"
    await message.reply(
        f"<b>{header} ᴄʟᴧiϻєᴅ!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🪙 +{coins:,} ᴄσiηs\n"
        f"📈 +{xp:,} xᴩ\n\n"
        f"🔥 sᴛʀєᴧᴋ: <b>{new_streak}</b> ᴅᴧʏs"
    )


# ═══ /performance ═══
@router.message(F.text.regexp(r"^/performance(\s|$)"))
async def cmd_performance(message: Message):
    if message.chat.type != "private":
        return await message.reply("📩 ᴜsє ᴛнis iη вσᴛ ᴅᴍ σηʟʏ.")

    import aiosqlite
    from config import DB_PATH
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """SELECT quiz_attempted, quiz_solved, word_attempted, word_solved,
                      number_attempted, number_guess
               FROM users WHERE user_id=?""",
            (message.from_user.id,)
        ) as cur:
            row = await cur.fetchone()

    if not row:
        return await message.reply("❌ ʀєɢisтєʀ ғiʀsт вʏ /start.")

    qa, qs, wa, ws, na, ng = row
    total_att = qa + wa + na
    total_solved = qs + ws + ng
    accuracy = round((total_solved / total_att) * 100, 1) if total_att else 0.0

    await message.reply(
        f"📊 <b>ᴍʏ ᴩєʀғσʀϻᴧηᴄє</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🧠 ǫᴜiᴢ ᴧттєϻᴩтєᴅ : <b>{qa}</b>\n"
        f"✅ ǫᴜiᴢ sσʟᴠєᴅ    : <b>{qs}</b>\n\n"
        f"🔤 ωσʀᴅ ᴧттєϻᴩтєᴅ : <b>{wa}</b>\n"
        f"🎯 ωσʀᴅ sσʟᴠєᴅ    : <b>{ws}</b>\n\n"
        f"🔢 ηᴜϻвєʀ ᴧттєϻᴩтєᴅ: <b>{na}</b>\n"
        f"🎲 ηᴜϻвєʀ ɢᴜєss   : <b>{ng}</b>\n\n"
        f"📈 ᴧᴄᴄᴜʀᴧᴄʏ     : <b>{accuracy}%</b>"
    )
