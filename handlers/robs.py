import random
from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message

from config import (
    ROB_NORMAL_PERCENT, ROB_PREMIUM_PERCENT, SHIELD_FREE_DAYS,
    SUPPORT_GROUP_NAME, GIVE_DEDUCTION_PERCENT,
)
from keyboards.main_menu import premium_kb
from utils.database import (
    get_or_create_user, add_coins, add_xp, is_premium, is_shielded,
    set_shield,
)

router = Router()


# ═══ /give ═══
@router.message(Command("give"))
async def cmd_give(message: Message, bot: Bot):
    if not message.reply_to_message or not message.reply_to_message.from_user:
        return await message.reply("❌ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜꜱᴇʀ ᴡɪᴛʜ <code>/give [ᴀᴍᴏᴜɴᴛ]</code>")

    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        return await message.reply("ᴜꜱᴀɢᴇ: <code>/give 10000</code> (ʀᴇᴘʟʏ ᴛᴏ ᴛᴀʀɢᴇᴛ)")

    sender = message.from_user
    receiver = message.reply_to_message.from_user
    amount = int(parts[1])

    if sender.id == receiver.id:
        return await message.reply("❌ ᴄᴀɴ'ᴛ ɢɪᴠᴇ ᴛᴏ ʏᴏᴜʀꜱᴇʟꜰ.")
    if receiver.is_bot:
        return await message.reply("❌ ᴄᴀɴ'ᴛ ɢɪᴠᴇ ᴛᴏ ᴀ ʙᴏᴛ.")
    if amount < 1:
        return await message.reply("❌ ᴀᴍᴏᴜɴᴛ ᴍᴜꜱᴛ ʙᴇ ᴀᴛ ʟᴇᴀꜱᴛ 1.")

    await get_or_create_user(sender.id, sender.username, sender.first_name)
    await get_or_create_user(receiver.id, receiver.username, receiver.first_name)

    import aiosqlite
    from config import DB_PATH
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT coins FROM users WHERE user_id=?", (sender.id,)) as cur:
            row = await cur.fetchone()
    sender_coins = row[0] if row else 0

    if sender_coins < amount:
        return await message.reply(
            f"❌ ɪɴꜱᴜꜰꜰɪᴄɪᴇɴᴛ ᴄᴏɪɴꜱ!\n\nʏᴏᴜ ʜᴀᴠᴇ: <b>{sender_coins:,}</b> 🪙"
        )

    deduction = (amount * GIVE_DEDUCTION_PERCENT) // 100
    received = amount - deduction

    await add_coins(sender.id, -amount)
    await add_coins(receiver.id, received)

    await message.reply(
        f"✅ <b>ᴄᴏɪɴꜱ ꜱᴇɴᴛ!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 {receiver.mention_html()} ɢᴀɪɴᴇᴅ <b>{received:,}</b> 🪙 "
        f"ᴀꜰᴛᴇʀ 10% ᴏꜰ ᴅᴇᴅᴜᴄᴛɪᴏɴ."
    )


# ═══ /robs ═══
@router.message(Command("robs"))
async def cmd_robs(message: Message, bot: Bot):
    if not message.reply_to_message or not message.reply_to_message.from_user:
        return await message.reply("❌ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜꜱᴇʀ ᴛᴏ ʀᴏʙ ᴛʜᴇᴍ.")

    robber = message.from_user
    victim = message.reply_to_message.from_user

    if robber.id == victim.id:
        return await message.reply("❌ ᴄᴀɴ'ᴛ ʀᴏʙ ʏᴏᴜʀꜱᴇʟꜰ.")
    if victim.is_bot:
        return await message.reply("❌ ᴄᴀɴ'ᴛ ʀᴏʙ ᴀ ʙᴏᴛ.")

    await get_or_create_user(robber.id, robber.username, robber.first_name)
    await get_or_create_user(victim.id, victim.username, victim.first_name)

    if await is_shielded(victim.id):
        return await message.reply(
            "🛡️ ᴛʜᴇ ᴛᴀʀɢᴇᴛᴇᴅ ᴠɪᴄᴛɪᴍ ɪꜱ ᴜɴᴅᴇʀ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ.\n"
            "ᴡᴀɪᴛ ᴛɪʟʟ ᴛʜᴇʏ ʀᴇᴍᴏᴠᴇ ᴛʜᴇɪʀ ꜱʜɪᴇʟᴅ."
        )

    import aiosqlite
    from config import DB_PATH
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT coins FROM users WHERE user_id=?", (victim.id,)) as cur:
            row = await cur.fetchone()
    victim_coins = row[0] if row else 0

    if victim_coins < 10:
        return await message.reply(f"❌ {victim.mention_html()} ʜᴀꜱ ɴᴏᴛʜɪɴɢ ᴡᴏʀᴛʜ ʀᴏʙʙɪɴɢ.")

    pct = ROB_PREMIUM_PERCENT if await is_premium(robber.id) else ROB_NORMAL_PERCENT
    stolen_base = int(victim_coins * pct / 100)

    if stolen_base < 1:
        return await message.reply("❌ ᴀᴍᴏᴜɴᴛ ᴛᴏᴏ ꜱᴍᴀʟʟ.")

    deduction = (stolen_base * GIVE_DEDUCTION_PERCENT) // 100
    robber_receives = stolen_base - deduction

    await add_coins(victim.id, -stolen_base)
    await add_coins(robber.id, robber_receives)

    xp_gain = random.randint(0, 10)
    await add_xp(robber.id, xp_gain)

    await message.reply(
        f"🪙 <b>ʀᴏʙ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 {robber.mention_html()} ɢᴀɪɴᴇᴅ <b>{robber_receives:,}</b> 🪙 "
        f"ᴀꜰᴛᴇʀ 10% ᴏꜰ ᴅᴇᴅᴜᴄᴛɪᴏɴ.\n"
        f"📈 xᴘ ɢᴀɪɴᴇᴅ: <b>+{xp_gain}</b>"
    )

    try:
        await bot.send_message(
            victim.id,
            f"⚠️ <b>ʏᴏᴜ ᴡᴇʀᴇ ʀᴏʙʙᴇᴅ!</b>\n\n"
            f"👤 ʀᴏʙʙᴇʀ: {robber.mention_html()}\n"
            f"💸 ꜱᴛᴏʟᴇɴ: <b>{stolen_base:,}</b> 🪙\n"
            f"📍 ɢʀᴏᴜᴘ: <b>{message.chat.title or SUPPORT_GROUP_NAME}</b>"
        )
    except Exception:
        pass


# ═══ /shield ═══
@router.message(Command("shield"))
async def cmd_shield(message: Message):
    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        return await message.reply(
            f"ᴜꜱᴀɢᴇ: <code>/shield 2</code>\n\n"
            f"🛡️ ꜰʀᴇᴇ ꜱʜɪᴇʟᴅ: {SHIELD_FREE_DAYS} ᴅᴀʏꜱ\nᴘʀᴇᴍɪᴜᴍ: ᴜᴘ ᴛᴏ 5 ᴅᴀʏꜱ"
        )
    days = int(parts[1])
    if days < 1:
        return await message.reply("❌ ɪɴᴠᴀʟɪᴅ ᴅᴀʏꜱ.")
    if days > SHIELD_FREE_DAYS:
        if not await is_premium(message.from_user.id):
            return await message.reply(
                f"❌ ᴍᴀx {SHIELD_FREE_DAYS} ᴅᴀʏꜱ ꜰʀᴇᴇ.\nᴜꜱᴇ /premium ꜰᴏʀ ᴇxᴛʀᴀ."
            )
    until = await set_shield(message.from_user.id, days)
    await message.reply(
        f"🛡️ <b>ꜱʜɪᴇʟᴅ ᴀᴄᴛɪᴠᴀᴛᴇᴅ!</b>\n\n"
        f"ᴘʀᴏᴛᴇᴄᴛᴇᴅ ꜰᴏʀ: <b>{days} ᴅᴀʏꜱ</b>\n"
        f"ᴜɴᴛɪʟ: {until.strftime('%Y-%m-%d %H:%M')} UTC"
    )


# ═══ /premium ═══
@router.message(Command("premium"))
async def cmd_premium(message: Message):
    text = (
        f"⭐ <b>ᴀꜱᴛʀᴀʟ ᴘʀᴇᴍɪᴜᴍ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎁 <b>ᴘʀᴇᴍɪᴜᴍ ʙᴇɴᴇꜰɪᴛꜱ:</b>\n"
        f"• ʀᴏʙ ᴅᴇᴅᴜᴄᴛɪᴏɴ: 10% → <b>5%</b>\n"
        f"• ᴅᴀɪʟʏ ʀᴇᴡᴀʀᴅ: 2000 → <b>5500 ᴄᴏɪɴꜱ</b>\n"
        f"• ᴅᴀɪʟʏ xᴘ: 150 → <b>350 xᴘ</b>\n"
        f"• ʟᴏɴɢᴇʀ ꜱʜɪᴇʟᴅ ᴅᴜʀᴀᴛɪᴏɴ\n\n"
        f"📦 <b>ᴘʟᴀɴꜱ:</b>\n"
        f"• 1 ᴍᴏɴᴛʜ — 90 ⭐\n"
        f"• 4 ᴍᴏɴᴛʜꜱ — 140 ⭐\n"
        f"• 12 ᴍᴏɴᴛʜꜱ — 175 ⭐\n\n"
        f"💫 ᴠɪᴀ ᴛᴇʟᴇɢʀᴀᴍ ꜱᴛᴀʀꜱ ᴛᴏ ᴛʜᴇ ᴏᴡɴᴇʀ."
    )
    await message.reply(text, reply_markup=premium_kb())
