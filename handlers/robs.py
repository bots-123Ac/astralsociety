import random
from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message

from config import (
    ROB_NORMAL_PERCENT, ROB_PREMIUM_PERCENT,
    SHIELD_NORMAL_MAX_DAYS, SHIELD_PREMIUM_MAX_DAYS,
    SUPPORT_GROUP_NAME, GIVE_DEDUCTION_PERCENT,
)
from utils.database import (
    get_or_create_user, add_coins, add_xp, is_premium, is_shielded,
    set_shield, shield_remaining, get_user_coins,
)

router = Router()


# ═══════════════════════════════════════════════
# /give [amount] — reply only
# ═══════════════════════════════════════════════
@router.message(Command("give"))
async def cmd_give(message: Message, bot: Bot):
    if not message.reply_to_message or not message.reply_to_message.from_user:
        return await message.reply(
            "❌ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜꜱᴇʀ ᴡɪᴛʜ <code>/give [ᴀᴍᴏᴜɴᴛ]</code>"
        )

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

    sender_coins = await get_user_coins(sender.id)

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


# ═══════════════════════════════════════════════
# /robs — reply only (full or specific amount)
# ═══════════════════════════════════════════════
@router.message(Command("robs"))
async def cmd_robs(message: Message, bot: Bot):
    if not message.reply_to_message or not message.reply_to_message.from_user:
        return await message.reply(
            "❌ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜꜱᴇʀ.\n\n"
            "📌 <b>ᴜꜱᴀɢᴇ:</b>\n"
            "• <code>/robs</code> — ꜰᴜʟʟ ʙᴀʟᴀɴᴄᴇ\n"
            "• <code>/robs 5000</code> — ꜱᴘᴇᴄɪꜰɪᴄ ᴀᴍᴏᴜɴᴛ"
        )

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

    victim_coins = await get_user_coins(victim.id)

    if victim_coins < 10:
        return await message.reply(
            f"❌ {victim.mention_html()} ʜᴀꜱ ɴᴏᴛʜɪɴɢ ᴡᴏʀᴛʜ ʀᴏʙʙɪɴɢ."
        )

    parts = message.text.split()
    if len(parts) >= 2 and parts[1].isdigit():
        base_amount = int(parts[1])
        if base_amount < 1:
            return await message.reply("❌ ɪɴᴠᴀʟɪᴅ ᴀᴍᴏᴜɴᴛ.")
        if base_amount > victim_coins:
            base_amount = victim_coins
    else:
        base_amount = victim_coins

    if base_amount < 1:
        return await message.reply("❌ ᴀᴍᴏᴜɴᴛ ᴛᴏᴏ ꜱᴍᴀʟʟ.")

    # Deduction based on robber's premium
    pct = ROB_PREMIUM_PERCENT if await is_premium(robber.id) else ROB_NORMAL_PERCENT
    deduction = (base_amount * pct) // 100
    robber_receives = base_amount - deduction

    await add_coins(victim.id, -base_amount)
    await add_coins(robber.id, robber_receives)

    xp_gain = random.randint(0, 10)
    await add_xp(robber.id, xp_gain)

    await message.reply(
        f"🪙 <b>ʀᴏʙ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 {robber.mention_html()} ɢᴀɪɴᴇᴅ <b>{robber_receives:,}</b> 🪙 "
        f"ᴀꜰᴛᴇʀ {pct}% ᴏꜰ ᴅᴇᴅᴜᴄᴛɪᴏɴ.\n"
        f"📈 xᴘ: <b>+{xp_gain}</b>"
    )

    # DM victim
    try:
        await bot.send_message(
            victim.id,
            f"⚠️ <b>ʏᴏᴜ ᴡᴇʀᴇ ʀᴏʙʙᴇᴅ!</b>\n\n"
            f"👤 ʀᴏʙʙᴇʀ: {robber.mention_html()}\n"
            f"💸 ꜱᴛᴏʟᴇɴ: <b>{base_amount:,}</b> 🪙\n"
            f"📍 ɢʀᴏᴜᴘ: <b>{message.chat.title or SUPPORT_GROUP_NAME}</b>"
        )
    except Exception:
        pass


# ═══════════════════════════════════════════════
# /shield [days]
# ═══════════════════════════════════════════════
@router.message(Command("shield"))
async def cmd_shield(message: Message):
    await get_or_create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
    )

    is_prem = await is_premium(message.from_user.id)
    max_days = SHIELD_PREMIUM_MAX_DAYS if is_prem else SHIELD_NORMAL_MAX_DAYS

    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        return await message.reply(
            f"ᴜꜱᴀɢᴇ: <code>/shield 2</code>\n\n"
            f"🛡️ ɴᴏʀᴍᴀʟ ᴍᴀx: {SHIELD_NORMAL_MAX_DAYS} ᴅᴀʏꜱ\n"
            f"⭐ ᴘʀᴇᴍɪᴜᴍ ᴍᴀx: {SHIELD_PREMIUM_MAX_DAYS} ᴅᴀʏꜱ"
        )

    days = int(parts[1])
    if days < 1:
        return await message.reply("❌ ɪɴᴠᴀʟɪᴅ ᴅᴀʏꜱ.")
    if days > max_days:
        msg = f"❌ ᴍᴀx {max_days} ᴅᴀʏꜱ ᴏɴʟʏ."
        if not is_prem:
            msg += "\n⭐ ᴜꜱᴇ /premium ꜰᴏʀ 5 ᴅᴀʏꜱ."
        return await message.reply(msg)

    until = await set_shield(message.from_user.id, days)
    await message.reply(
        f"🛡️ <b>ꜱʜɪᴇʟᴅ ᴀᴄᴛɪᴠᴀᴛᴇᴅ!</b>\n\n"
        f"ᴘʀᴏᴛᴇᴄᴛᴇᴅ ꜰᴏʀ: <b>{days} ᴅᴀʏꜱ</b>\n"
        f"ᴜɴᴛɪʟ: {until.strftime('%Y-%m-%d %H:%M')} UTC"
    )


# ═══════════════════════════════════════════════
# /shieldcheck
# ═══════════════════════════════════════════════
@router.message(Command("shieldcheck"))
async def cmd_shieldcheck(message: Message):
    await get_or_create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
    )

    checker = message.from_user
    checker_premium = await is_premium(checker.id)

    # Normal user → only own shield
    if not checker_premium:
        rem = await shield_remaining(checker.id)
        if rem <= 0:
            return await message.reply(
                "🛡️ ʏᴏᴜ ᴅᴏ ɴᴏᴛ ʜᴀᴠᴇ ᴀɴ ᴀᴄᴛɪᴠᴇ ꜱʜɪᴇʟᴅ.\n\n"
                "⭐ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀꜱ ᴄᴀɴ ᴄʜᴇᴄᴋ ᴏᴛʜᴇʀꜱ' ꜱʜɪᴇʟᴅ ᴛɪᴍᴇ."
            )
        return await message.reply(f"🛡️ ʏᴏᴜʀ ꜱʜɪᴇʟᴅ: <b>{rem} ᴅᴀʏꜱ ʟᴇꜰᴛ</b>")

    # Premium user
    if not message.reply_to_message or not message.reply_to_message.from_user:
        rem = await shield_remaining(checker.id)
        if rem <= 0:
            return await message.reply("🛡️ ʏᴏᴜ ᴅᴏ ɴᴏᴛ ʜᴀᴠᴇ ᴀɴ ᴀᴄᴛɪᴠᴇ ꜱʜɪᴇʟᴅ.")
        return await message.reply(f"🛡️ ʏᴏᴜʀ ꜱʜɪᴇʟᴅ: <b>{rem} ᴅᴀʏꜱ ʟᴇꜰᴛ</b>")

    target = message.reply_to_message.from_user

    if await is_premium(target.id):
        return await message.reply(
            "❌ ᴄᴀɴ'ᴛ ᴄʜᴇᴄᴋ ᴀɴᴏᴛʜᴇʀ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀ'ꜱ ꜱʜɪᴇʟᴅ."
        )

    rem = await shield_remaining(target.id)
    if rem <= 0:
        return await message.reply(
            f"🛡️ {target.mention_html()}: <b>ɴᴏ ᴀᴄᴛɪᴠᴇ ꜱʜɪᴇʟᴅ</b>"
        )
    await message.reply(
        f"🛡️ {target.mention_html()}: <b>{rem} ᴅᴀʏꜱ ʟᴇꜰᴛ</b>"
    )
