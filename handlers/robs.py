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
    set_shield, shield_remaining, shield_remaining_seconds,
    format_shield_time, get_user_coins,
)

router = Router()


# ═══════════════════════════════════════════════
# /gives [amount] — reply only (transfer, no leaderboard log)
# ═══════════════════════════════════════════════
@router.message(Command("gives"))
async def cmd_gives(message: Message, bot: Bot):
    if not message.reply_to_message or not message.reply_to_message.from_user:
        return await message.reply(
            "❌ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜꜱᴇʀ ᴡɪᴛʜ <code>/gives [ᴀᴍᴏᴜɴᴛ]</code>"
        )

    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        return await message.reply(
            "ᴜꜱᴀɢᴇ: <code>/gives 10000</code>\n(ʀᴇᴘʟʏ ᴛᴏ ᴛᴀʀɢᴇᴛ ᴜꜱᴇʀ)"
        )

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
            f"⚠️ <b>ʏᴏᴜ ʜᴀᴠᴇ ᴏɴʟʏ {sender_coins:,} ᴄᴏɪɴꜱ</b>"
        )

    deduction = (amount * GIVE_DEDUCTION_PERCENT) // 100
    received = amount - deduction

    # is_earning=False → don't log to leaderboard (it's a transfer)
    await add_coins(sender.id, -amount, is_earning=False)
    await add_coins(receiver.id, received, is_earning=False)

    await message.reply(
        f"✅ <b>ᴄᴏɪɴꜱ ꜱᴇɴᴛ!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 {receiver.mention_html()} ɢᴀɪɴᴇᴅ <b>{received:,}</b> 🪙 "
        f"ᴀꜰᴛᴇʀ 10% ᴏꜰ ᴅᴇᴅᴜᴄᴛɪᴏɴ."
    )

    group_name = message.chat.title or SUPPORT_GROUP_NAME
    try:
        await bot.send_message(
            receiver.id,
            f"💸 <b>ꜱᴏᴍᴇᴏɴᴇ ɢᴀᴠᴇ ʏᴏᴜ ᴍᴏɴᴇʏ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 ɢɪᴠᴇʀ: {sender.mention_html()}\n"
            f"💰 ᴀᴍᴏᴜɴᴛ: <b>{received:,}</b> 🪙\n"
            f"📍 ɢʀᴏᴜᴘ: <b>{group_name}</b>"
        )
    except Exception:
        pass


# ═══════════════════════════════════════════════
# /robs [amount] — reply only (transfer, no leaderboard log)
# ═══════════════════════════════════════════════
@router.message(Command("robs"))
async def cmd_robs(message: Message, bot: Bot):
    if not message.reply_to_message or not message.reply_to_message.from_user:
        return await message.reply(
            "❌ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜꜱᴇʀ.\n\n"
            "📌 <b>ᴜꜱᴀɢᴇ:</b>\n"
            "• <code>/robs 5000</code> — ʀᴏʙ ꜱᴘᴇᴄɪꜰɪᴄ ᴀᴍᴏᴜɴᴛ"
        )

    robber = message.from_user
    victim = message.reply_to_message.from_user

    if robber.id == victim.id:
        return await message.reply("❌ ᴄᴀɴ'ᴛ ʀᴏʙ ʏᴏᴜʀꜱᴇʟꜰ.")
    if victim.is_bot:
        return await message.reply("❌ ᴄᴀɴ'ᴛ ʀᴏʙ ᴀ ʙᴏᴛ.")

    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        return await message.reply(
            "❌ ᴀᴍᴏᴜɴᴛ ʀᴇǫᴜɪʀᴇᴅ!\n\n"
            "ᴜꜱᴀɢᴇ: <code>/robs 5000</code> (ʀᴇᴘʟʏ ᴛᴏ ᴛᴀʀɢᴇᴛ)"
        )

    amount = int(parts[1])
    if amount < 1:
        return await message.reply("❌ ɪɴᴠᴀʟɪᴅ ᴀᴍᴏᴜɴᴛ.")

    await get_or_create_user(robber.id, robber.username, robber.first_name)
    await get_or_create_user(victim.id, victim.username, victim.first_name)

    if await is_shielded(victim.id):
        return await message.reply(
            "🛡️ ᴛʜᴇ ᴛᴀʀɢᴇᴛᴇᴅ ᴠɪᴄᴛɪᴍ ɪꜱ ᴜɴᴅᴇʀ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ.\n"
            "ᴡᴀɪᴛ ᴛɪʟʟ ᴛʜᴇʏ ʀᴇᴍᴏᴠᴇ ᴛʜᴇɪʀ ꜱʜɪᴇʟᴅ."
        )

    victim_coins = await get_user_coins(victim.id)

    if victim_coins < 1:
        return await message.reply(
            f"⚠️ <b>{victim.mention_html()} ʜᴀꜱ ᴏɴʟʏ 0 ᴄᴏɪɴꜱ</b>"
        )

    if amount > victim_coins:
        return await message.reply(
            f"⚠️ <b>{victim.mention_html()} ʜᴀꜱ ᴏɴʟʏ {victim_coins:,} ᴄᴏɪɴꜱ</b>\n\n"
            f"ʏᴏᴜ ᴛʀɪᴇᴅ ᴛᴏ ʀᴏʙ <b>{amount:,}</b> ᴄᴏɪɴꜱ."
        )

    pct = ROB_PREMIUM_PERCENT if await is_premium(robber.id) else ROB_NORMAL_PERCENT
    deduction = (amount * pct) // 100
    robber_receives = amount - deduction

    # is_earning=False → don't log to leaderboard (transfer)
    await add_coins(victim.id, -amount, is_earning=False)
    await add_coins(robber.id, robber_receives, is_earning=False)

    xp_gain = random.randint(0, 10)
    await add_xp(robber.id, xp_gain)

    await message.reply(
        f"🪙 <b>ʀᴏʙ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 {robber.mention_html()} ɢᴀɪɴᴇᴅ <b>{robber_receives:,}</b> 🪙 "
        f"ᴀꜰᴛᴇʀ {pct}% ᴏꜰ ᴅᴇᴅᴜᴄᴛɪᴏɴ.\n"
        f"📈 xᴘ: <b>+{xp_gain}</b>"
    )

    group_name = message.chat.title or SUPPORT_GROUP_NAME
    try:
        await bot.send_message(
            victim.id,
            f"⚠️ <b>ʏᴏᴜ ᴡᴇʀᴇ ʀᴏʙʙᴇᴅ!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 ʀᴏʙʙᴇʀ: {robber.mention_html()}\n"
            f"💸 ꜱᴛᴏʟᴇɴ: <b>{amount:,}</b> 🪙\n"
            f"📍 ɢʀᴏᴜᴘ: <b>{group_name}</b>"
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

    # ═══ Check if already shielded ═══
    remaining_sec = await shield_remaining_seconds(message.from_user.id)
    if remaining_sec > 0:
        return await message.reply(
            f"🛡️ <b>ʏᴏᴜ ᴀʀᴇ ᴀʟʀᴇᴀᴅʏ ᴘʀᴏᴛᴇᴄᴛᴇᴅ.</b>\n"
            f"⏳ ʀᴇᴍᴀɪɴɪɴɢ: <b>{format_shield_time(remaining_sec)}</b>"
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

    # ═══ If checking own shield and already active ═══
    has_target = message.reply_to_message and message.reply_to_message.from_user

    if not checker_premium and not has_target:
        rem_sec = await shield_remaining_seconds(checker.id)
        if rem_sec <= 0:
            return await message.reply(
                "🛡️ ʏᴏᴜ ᴅᴏ ɴᴏᴛ ʜᴀᴠᴇ ᴀɴ ᴀᴄᴛɪᴠᴇ ꜱʜɪᴇʟᴅ.\n\n"
                "⭐ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀꜱ ᴄᴀɴ ᴄʜᴇᴄᴋ ᴏᴛʜᴇʀꜱ' ꜱʜɪᴇʟᴅ ᴛɪᴍᴇ."
            )
        return await message.reply(
            f"🛡️ <b>ʏᴏᴜ ᴀʀᴇ ᴀʟʀᴇᴀᴅʏ ᴘʀᴏᴛᴇᴄᴛᴇᴅ.</b>\n"
            f"⏳ ʀᴇᴍᴀɪɴɪɴɢ: <b>{format_shield_time(rem_sec)}</b>"
        )

    # Premium user / no target → own shield
    if not has_target:
        rem_sec = await shield_remaining_seconds(checker.id)
        if rem_sec <= 0:
            return await message.reply("🛡️ ʏᴏᴜ ᴅᴏ ɴᴏᴛ ʜᴀᴠᴇ ᴀɴ ᴀᴄᴛɪᴠᴇ ꜱʜɪᴇʟᴅ.")
        return await message.reply(
            f"🛡️ <b>ʏᴏᴜ ᴀʀᴇ ᴀʟʀᴇᴀᴅʏ ᴘʀᴏᴛᴇᴄᴛᴇᴅ.</b>\n"
            f"⏳ ʀᴇᴍᴀɪɴɪɴɢ: <b>{format_shield_time(rem_sec)}</b>"
        )

    # Target given
    target = message.reply_to_message.from_user

    if await is_premium(target.id):
        return await message.reply(
            "❌ ᴄᴀɴ'ᴛ ᴄʜᴇᴄᴋ ᴀɴᴏᴛʜᴇʀ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀ'ꜱ ꜱʜɪᴇʟᴅ."
        )

    rem_sec = await shield_remaining_seconds(target.id)
    if rem_sec <= 0:
        return await message.reply(
            f"🛡️ {target.mention_html()}: <b>ɴᴏ ᴀᴄᴛɪᴠᴇ ꜱʜɪᴇʟᴅ</b>"
        )
    await message.reply(
        f"🛡️ {target.mention_html()}:\n"
        f"⏳ <b>{format_shield_time(rem_sec)}</b> ʀᴇᴍᴀɪɴɪɴɢ"
    )
