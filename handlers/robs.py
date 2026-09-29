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
    set_shield, shield_remaining_seconds, format_shield_time, get_user_coins,
)

router = Router()


@router.message(Command("gives"))
async def cmd_gives(message: Message, bot: Bot):
    if not message.reply_to_message or not message.reply_to_message.from_user:
        return await message.reply("❌ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜꜱᴇʀ ᴡɪᴛʜ <code>/gives [ᴀᴍᴏᴜɴᴛ]</code>")
    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        return await message.reply("ᴜꜱᴀɢᴇ: <code>/gives 10000</code>\n(ʀᴇᴘʟʏ ᴛᴏ ᴛᴀʀɢᴇᴛ)")
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
    sc = await get_user_coins(sender.id)
    if sc < amount:
        return await message.reply(f"⚠️ <b>ʏᴏᴜ ʜᴀᴠᴇ ᴏɴʟʏ {sc:,} ᴄᴏɪɴꜱ</b>")
    ded = (amount * GIVE_DEDUCTION_PERCENT) // 100
    recv = amount - ded
    await add_coins(sender.id, -amount, is_earning=False)
    await add_coins(receiver.id, recv, is_earning=False)
    await message.reply(
        f"✅ <b>ᴄᴏɪɴꜱ ꜱᴇɴᴛ!</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 {receiver.mention_html()} ɢᴀɪɴᴇᴅ <b>{recv:,}</b> 🪙 ᴀꜰᴛᴇʀ 10% ᴅᴇᴅᴜᴄᴛɪᴏɴ."
    )
    try:
        await bot.send_message(
            receiver.id,
            f"💸 <b>ꜱᴏᴍᴇᴏɴᴇ ɢᴀᴠᴇ ʏᴏᴜ ᴍᴏɴᴇʏ</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 ɢɪᴠᴇʀ: {sender.mention_html()}\n💰 ᴀᴍᴏᴜɴᴛ: <b>{recv:,}</b> 🪙\n"
            f"📍 ɢʀᴏᴜᴘ: <b>{message.chat.title or SUPPORT_GROUP_NAME}</b>"
        )
    except Exception:
        pass


@router.message(Command("robs"))
async def cmd_robs(message: Message, bot: Bot):
    if not message.reply_to_message or not message.reply_to_message.from_user:
        return await message.reply("❌ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜꜱᴇʀ.\n\nᴜꜱᴀɢᴇ: <code>/robs 5000</code>")
    robber = message.from_user
    victim = message.reply_to_message.from_user
    if robber.id == victim.id:
        return await message.reply("❌ ᴄᴀɴ'ᴛ ʀᴏʙ ʏᴏᴜʀꜱᴇʟꜰ.")
    if victim.is_bot:
        return await message.reply("❌ ᴄᴀɴ'ᴛ ʀᴏʙ ᴀ ʙᴏᴛ.")
    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        return await message.reply("❌ ᴀᴍᴏᴜɴᴛ ʀᴇǫᴜɪʀᴇᴅ!\nᴜꜱᴀɢᴇ: <code>/robs 5000</code>")
    amount = int(parts[1])
    if amount < 1:
        return await message.reply("❌ ɪɴᴠᴀʟɪᴅ ᴀᴍᴏᴜɴᴛ.")
    await get_or_create_user(robber.id, robber.username, robber.first_name)
    await get_or_create_user(victim.id, victim.username, victim.first_name)
    if await is_shielded(victim.id):
        return await message.reply("🛡️ ᴛᴀʀɢᴇᴛ ɪꜱ ᴜɴᴅᴇʀ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ.\nᴡᴀɪᴛ ᴛɪʟʟ ꜱʜɪᴇʟᴅ ᴇxᴘɪʀᴇꜱ.")
    vc = await get_user_coins(victim.id)
    if vc < 1:
        return await message.reply(f"⚠️ <b>{victim.mention_html()} ʜᴀꜱ ᴏɴʟʏ 0 ᴄᴏɪɴꜱ</b>")
    if amount > vc:
        return await message.reply(
            f"⚠️ <b>{victim.mention_html()} ʜᴀꜱ ᴏɴʟʏ {vc:,} ᴄᴏɪɴꜱ</b>\n\n"
            f"ʏᴏᴜ ᴛʀɪᴇᴅ ᴛᴏ ʀᴏʙ <b>{amount:,}</b> ᴄᴏɪɴꜱ."
        )
    pct = ROB_PREMIUM_PERCENT if await is_premium(robber.id) else ROB_NORMAL_PERCENT
    ded = (amount * pct) // 100
    recv = amount - ded
    await add_coins(victim.id, -amount, is_earning=False)
    await add_coins(robber.id, recv, is_earning=False)
    xp = random.randint(0, 10)
    await add_xp(robber.id, xp)
    await message.reply(
        f"🪙 <b>ʀᴏʙ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ!</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 {robber.mention_html()} ɢᴀɪɴᴇᴅ <b>{recv:,}</b> 🪙 ᴀꜰᴛᴇʀ {pct}% ᴅᴇᴅᴜᴄᴛɪᴏɴ.\n"
        f"📈 xᴘ: <b>+{xp}</b>"
    )
    try:
        await bot.send_message(
            victim.id,
            f"⚠️ <b>ʏᴏᴜ ᴡᴇʀᴇ ʀᴏʙʙᴇᴅ!</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 ʀᴏʙʙᴇʀ: {robber.mention_html()}\n💸 ꜱᴛᴏʟᴇɴ: <b>{amount:,}</b> 🪙\n"
            f"📍 ɢʀᴏᴜᴘ: <b>{message.chat.title or SUPPORT_GROUP_NAME}</b>"
        )
    except Exception:
        pass


@router.message(Command("shield"))
async def cmd_shield(message: Message):
    await get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    rem = await shield_remaining_seconds(message.from_user.id)
    if rem > 0:
        return await message.reply(
            f"🛡️ <b>ʏᴏᴜ ᴀʀᴇ ᴀʟʀᴇᴀᴅʏ ᴘʀᴏᴛᴇᴄᴛᴇᴅ.</b>\n⏳ ʀᴇᴍᴀɪɴɪɴɢ: <b>{format_shield_time(rem)}</b>"
        )
    is_prem = await is_premium(message.from_user.id)
    max_d = SHIELD_PREMIUM_MAX_DAYS if is_prem else SHIELD_NORMAL_MAX_DAYS
    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        return await message.reply(
            f"ᴜꜱᴀɢᴇ: <code>/shield 2</code>\n\n"
            f"🛡️ ɴᴏʀᴍᴀʟ ᴍᴀx: {SHIELD_NORMAL_MAX_DAYS} ᴅᴀʏꜱ\n⭐ ᴘʀᴇᴍɪᴜᴍ ᴍᴀx: {SHIELD_PREMIUM_MAX_DAYS} ᴅᴀʏꜱ"
        )
    days = int(parts[1])
    if days < 1:
        return await message.reply("❌ ɪɴᴠᴀʟɪᴅ ᴅᴀʏꜱ.")
    if days > max_d:
        m = f"❌ ᴍᴀx {max_d} ᴅᴀʏꜱ ᴏɴʟʏ."
        if not is_prem:
            m += "\n⭐ ᴜꜱᴇ /premium ꜰᴏʀ 5 ᴅᴀʏꜱ."
        return await message.reply(m)
    until = await set_shield(message.from_user.id, days)
    await message.reply(
        f"🛡️ <b>ꜱʜɪᴇʟᴅ ᴀᴄᴛɪᴠᴀᴛᴇᴅ!</b>\n\nᴘʀᴏᴛᴇᴄᴛᴇᴅ: <b>{days} ᴅᴀʏꜱ</b>\nᴜɴᴛɪʟ: {until.strftime('%Y-%m-%d %H:%M')} UTC"
    )


@router.message(Command("shieldcheck"))
async def cmd_shieldcheck(message: Message):
    await get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    prem = await is_premium(message.from_user.id)
    has_t = message.reply_to_message and message.reply_to_message.from_user

    if not has_t:
        rem = await shield_remaining_seconds(message.from_user.id)
        if rem <= 0:
            if not prem:
                return await message.reply("🛡️ ɴᴏ ᴀᴄᴛɪᴠᴇ ꜱʜɪᴇʟᴅ.\n\n⭐ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀꜱ ᴄᴀɴ ᴄʜᴇᴄᴋ ᴏᴛʜᴇʀꜱ' ꜱʜɪᴇʟᴅ.")
            return await message.reply("🛡️ ɴᴏ ᴀᴄᴛɪᴠᴇ ꜱʜɪᴇʟᴅ.")
        return await message.reply(
            f"🛡️ <b>ʏᴏᴜ ᴀʀᴇ ᴀʟʀᴇᴀᴅʏ ᴘʀᴏᴛᴇᴄᴛᴇᴅ.</b>\n⏳ ʀᴇᴍᴀɪɴɪɴɢ: <b>{format_shield_time(rem)}</b>"
        )

    target = message.reply_to_message.from_user
    if await is_premium(target.id):
        return await message.reply("❌ ᴄᴀɴ'ᴛ ᴄʜᴇᴄᴋ ᴀɴᴏᴛʜᴇʀ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀ'ꜱ ꜱʜɪᴇʟᴅ.")
    rem = await shield_remaining_seconds(target.id)
    if rem <= 0:
        return await message.reply(f"🛡️ {target.mention_html()}: ɴᴏ ᴀᴄᴛɪᴠᴇ ꜱʜɪᴇʟᴅ")
    await message.reply(
        f"🛡️ {target.mention_html()}:\n⏳ <b>{format_shield_time(rem)}</b> ʀᴇᴍᴀɪɴɪɴɢ"
    )
