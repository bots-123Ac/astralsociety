import random
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest

from config import (
    ROB_NORMAL_PERCENT, ROB_PREMIUM_PERCENT, SHIELD_FREE_DAYS,
    PREMIUM_PLANS, SUPPORT_GROUP_NAME,
)
from keyboards.main_menu import premium_kb, back_main_kb
from utils.database import (
    get_or_create_user, add_coins, add_xp, is_premium, is_shielded,
    set_shield, shield_remaining,
)
from utils.styler import fancy

router = Router()


# ═══ /robs (reply only) ═══
@router.message(Command("robs"))
async def cmd_robs(message: Message, bot: Bot):
    if not message.reply_to_message or not message.reply_to_message.from_user:
        return await message.reply("❌ ʀєᴩʟʏ тσ ᴧ ᴜsєʀ's ϻєssᴧɢє тσ ʀσв тнєϻ.")

    robber = message.from_user
    victim = message.reply_to_message.from_user

    if robber.id == victim.id:
        return await message.reply("❌ ʏσᴜ ᴄᴧη'т ʀσв ʏσᴜʀsєʟғ.")
    if victim.is_bot:
        return await message.reply("❌ ʏσᴜ ᴄᴧη'т ʀσв ᴧ вσᴛ.")

    # Register both
    await get_or_create_user(robber.id, robber.username, robber.first_name)
    await get_or_create_user(victim.id, victim.username, victim.first_name)

    # Check victim shield
    if await is_shielded(victim.id):
        return await message.reply(
            "🛡️ тнє тᴧʀɢєтєᴅ ᴠiᴄтiϻ is ᴜηᴅєʀ ᴩʀσтєᴄтiση.\n"
            "ᴡᴧiт тiʟʟ тнєʏ ʀєϻσᴠє тнєiʀ sнiєʟᴅ."
        )

    # Fetch victim coins
    import aiosqlite
    from config import DB_PATH
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT coins FROM users WHERE user_id=?", (victim.id,)) as cur:
            row = await cur.fetchone()
    victim_coins = row[0] if row else 0

    if victim_coins < 10:
        return await message.reply(
            f"❌ {victim.mention_html()} нᴧs ησтнiηɢ ωσʀтн ʀσввiηɢ."
        )

    # Determine %
    pct = ROB_PREMIUM_PERCENT if await is_premium(robber.id) else ROB_NORMAL_PERCENT
    amount = int(victim_coins * pct / 100)
    if amount < 1:
        return await message.reply("❌ ᴧϻσᴜηт тσσ sϻᴧʟʟ.")

    await add_coins(victim.id, -amount)
    await add_coins(robber.id, amount)
    xp_gain = random.randint(0, 20)
    await add_xp(robber.id, xp_gain)

    await message.reply(
        f"🪙 <b>ʀσв sᴜᴄᴄєssғᴜʟ!</b>\n\n"
        f"👤 ᴠiᴄтiϻ: {victim.mention_html()}\n"
        f"💸 sтσʟєη: <b>{amount:,} ᴄσiηs</b>\n"
        f"📈 xᴩ ɢᴧiηєᴅ: <b>+{xp_gain}</b>"
    )

    # DM to victim
    try:
        await bot.send_message(
            victim.id,
            f"⚠️ <b>ʏσᴜ ωєʀє ʀσввєᴅ!</b>\n\n"
            f"👤 ʀσввєʀ: {robber.mention_html()}\n"
            f"💸 ᴧϻσᴜηт sтσʟєη: <b>{amount:,} ᴄσiηs</b>\n"
            f"📍 ɢʀσᴜᴩ: <b>{message.chat.title or SUPPORT_GROUP_NAME}</b>"
        )
    except Exception:
        pass


# ═══ /shield ═══
@router.message(Command("shield"))
async def cmd_shield(message: Message):
    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        return await message.reply(
            f"ᴜsᴧɢє: <code>/shield 2</code>\n\n"
            f"🛡️ ғʀєє sнiєʟᴅ: {SHIELD_FREE_DAYS} ᴅᴧʏs\n"
            f"ᴩʀєϻiᴜϻ: ᴜᴩ тσ 5 ᴅᴧʏs"
        )
    days = int(parts[1])
    if days < 1:
        return await message.reply("❌ iηᴠᴧʟiᴅ ᴅᴧʏs.")
    if days > SHIELD_FREE_DAYS:
        if not await is_premium(message.from_user.id):
            return await message.reply(
                f"❌ ϻᴧxiϻᴜϻ {SHIELD_FREE_DAYS} ᴅᴧʏs ғʀєє.\n"
                f"ᴜsє /premium ғσʀ ᴇxᴛʀᴀ ᴅᴧʏs."
            )
    until = await set_shield(message.from_user.id, days)
    await message.reply(
        f"🛡️ <b>sнiєʟᴅ ᴧᴄтiᴠᴧтєᴅ!</b>\n\n"
        f"ᴩʀσтєᴄтєᴅ ғσʀ: <b>{days} ᴅᴧʏs</b>\n"
        f"ᴜηтiʟ: {until.strftime('%Y-%m-%d %H:%M')} UTC"
    )


# ═══ /premium ═══
@router.message(Command("premium"))
async def cmd_premium(message: Message):
    text = (
        f"⭐ <b>ᴧsᴛʀᴧʟ ᴩʀєϻiᴜϻ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎁 <b>ᴩʀєϻiᴜϻ ʙєηєғiтs:</b>\n"
        f"• ʀσв ᴅєᴅᴜᴄтiση: 10% → <b>5%</b>\n"
        f"• ᴅᴧiʟʏ ʀєωᴧʀᴅ: 2000 → <b>5500 ᴄσiηs</b>\n"
        f"• ᴅᴧiʟʏ xᴩ: 150 → <b>350 xᴩ</b>\n"
        f"• ʟσηɢєʀ sнiєʟᴅ ᴅᴜʀᴧтiση\n\n"
        f"📦 <b>ᴩʟᴧηs:</b>\n"
        f"• 1 ϻσηтн — 90 ⭐\n"
        f"• 4 ϻσηтнs — 140 ⭐\n"
        f"• 12 ϻσηтнs — 175 ⭐\n\n"
        f"💫 sтᴧʀs ѕєηᴅ кᴧʀηє кє ʙᴧᴅ ᴧᴅϻɪη sє ᴄσηтᴧᴄт кᴧʀєɪη.\n"
        f"(ᴏᴡηєʀ ɪᴅ ᴩє sтᴧʀs внєᴊєɪη)"
    )
    await message.reply(text, reply_markup=premium_kb())
