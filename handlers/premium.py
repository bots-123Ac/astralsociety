from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
)
from datetime import datetime

from config import PREMIUM_PLANS, OWNER_IDS
from utils.database import (
    get_or_create_user, get_premium_status, deduct_gems, set_premium,
    get_pool, set_custom_emoji, get_custom_emoji,
)
from utils.checks import dm_only

router = Router()


# ═══════════════════════════════════════════════
# KEYBOARDS
# ═══════════════════════════════════════════════
def premium_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 ᴡᴇᴇᴋ — 1,000 💎", callback_data="prem_buy:1w")],
        [InlineKeyboardButton(text="1 ᴍᴏɴᴛʜ — 10,000 💎", callback_data="prem_buy:1m")],
        [InlineKeyboardButton(text="1 ʏᴇᴀʀ — 100,000 💎", callback_data="prem_buy:1y")],
        [InlineKeyboardButton(text="🎨 sᴇᴛ ᴇᴍᴏᴊɪ", callback_data="prem_setemoji")],
        [InlineKeyboardButton(text="↩️ ʙᴀᴄᴋ", callback_data="menu:main")],
    ])


def premium_main_text() -> str:
    return (
        f"⭐ <b>ᴀꜱᴛʀᴀʟ ᴘʀᴇᴍɪᴜᴍ ꜱʜᴏᴘ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💎 ᴘᴜʀᴄʜᴀꜱᴇ ᴡɪᴛʜ ɢᴇᴍꜱ\n\n"
        f"🎁 <b>ᴘʀᴇᴍɪᴜᴍ ʙᴇɴᴇꜰɪᴛꜱ:</b>\n"
        f"• ʀᴏʙ ʟᴏꜱꜱ: 10% → <b>5%</b>\n"
        f"• ᴅᴀɪʟʏ ʀᴇᴡᴀʀᴅ: 2000 → <b>5000 ᴄᴏɪɴꜱ</b>\n"
        f"• ᴅᴀɪʟʏ xᴘ: 150 → <b>350 xᴘ</b>\n"
        f"• ꜱʜɪᴇʟᴅ ᴅᴜʀᴀᴛɪᴏɴ: 2 → <b>5 ᴅᴀʏꜱ</b>\n"
        f"• ʀᴏʙ ʟɪᴍɪᴛ: 15ᴋ → <b>100ᴋ</b>\n"
        f"• ᴘʀᴇᴍɪᴜᴍ ᴘʀᴏꜰɪʟᴇ ꜱᴛʏʟᴇ\n"
        f"• ᴠɪᴇᴡ ᴏᴛʜᴇʀꜱ' ꜱʜɪᴇʟᴅ ᴛɪᴍᴇ\n"
        f"• 🎨 <b>ᴄᴜꜱᴛᴏᴍ ᴇᴍᴏᴊɪ</b> (ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ)\n\n"
        f"💫 ᴄʜᴏᴏꜱᴇ ᴀ ᴘʟᴀɴ:"
    )


# ═══════════════════════════════════════════════
# /premium — Shop
# ═══════════════════════════════════════════════
@router.message(F.text.regexp(r"^/premium(@\w+)?(\s|$)"))
@dm_only
async def cmd_premium(message: Message):
    await get_or_create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
    )

    if message.from_user.id in OWNER_IDS:
        return await message.answer(
            f"👑 <b>ᴏᴡɴᴇʀ ᴀᴄᴄᴇꜱꜱ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"ʏᴏᴜ ᴀʀᴇ ᴀ <b>ʙᴏᴛ ᴏᴡɴᴇʀ</b>!\n\n"
            f"✅ ᴘʀᴇᴍɪᴜᴍ: <b>ᴜɴʟɪᴍɪᴛᴇᴅ</b>\n"
            f"♾️ ᴇxᴘɪʀᴇꜱ: <b>ɴᴇᴠᴇʀ</b>\n\n"
            f"🎨 ᴄᴜꜱᴛᴏᴍ ᴇᴍᴏᴊɪ ꜱᴇᴛ ᴋᴀʀɴᴇ ᴋᴇ ʟɪʏᴇ: /setemoji",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="↩️ ᴍᴀɪɴ ᴍᴇɴᴜ", callback_data="menu:main")]
            ])
        )

    await message.answer(premium_main_text(), reply_markup=premium_menu_kb())


# ═══════════════════════════════════════════════
# BUY PREMIUM
# ═══════════════════════════════════════════════
@router.callback_query(F.data.startswith("prem_buy:"))
async def cb_prem_buy(cb: CallbackQuery):
    plan_key = cb.data.split(":")[1]
    plan = PREMIUM_PLANS.get(plan_key)
    if not plan:
        return await cb.answer("ɪɴᴠᴀʟɪᴅ ᴘʟᴀɴ.", show_alert=True)

    user_id = cb.from_user.id

    if user_id in OWNER_IDS:
        return await cb.answer(
            "👑 ʏᴏᴜ ᴀʀᴇ ᴀ ʙᴏᴛ ᴏᴡɴᴇʀ!\nᴘʀᴇᴍɪᴜᴍ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴜɴʟɪᴍɪᴛᴇᴅ ꜰᴏʀ ʏᴏᴜ.",
            show_alert=True
        )

    is_active, expires_at, days_left = await get_premium_status(user_id)
    if is_active:
        return await cb.answer(
            f"⚠️ ʏᴏᴜ ᴀʀᴇ ᴀʟʀᴇᴀᴅʏ ᴘʀᴇᴍɪᴜᴍ!\nᴇxᴘɪʀᴇꜱ ɪɴ {days_left} ᴅᴀʏꜱ.",
            show_alert=True
        )

    pool = await get_pool()
    current_gems = await pool.fetchval(
        "SELECT gems FROM users WHERE user_id = $1", user_id
    )
    current_gems = current_gems or 0

    if current_gems < plan["gems"]:
        return await cb.answer(
            f"❌ ɪɴꜱᴜꜰꜰɪᴄɪᴇɴᴛ ɢᴇᴍꜱ!\n\nʏᴏᴜ ʜᴀᴠᴇ: {current_gems:,} 💎\nɴᴇᴇᴅ: {plan['gems']:,} 💎",
            show_alert=True
        )

    ok = await deduct_gems(user_id, plan["gems"])
    if not ok:
        return await cb.answer("❌ ᴛʀᴀɴꜱᴀᴄᴛɪᴏɴ ꜰᴀɪʟᴇᴅ.", show_alert=True)

    until = await set_premium(user_id, plan["days"])

    await cb.message.edit_text(
        f"✅ <b>ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴛɪᴠᴀᴛᴇᴅ!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⭐ ᴘʟᴀɴ: <b>{plan['label']}</b>\n"
        f"💎 ᴘᴀɪᴅ: <b>{plan['gems']:,} ɢᴇᴍꜱ</b>\n"
        f"📅 ᴠᴀʟɪᴅ ᴜɴᴛɪʟ: <b>{until.strftime('%Y-%m-%d %H:%M')} UTC</b>\n\n"
        f"🎁 ᴇɴᴊᴏʏ ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ʙᴇɴᴇꜰɪᴛꜱ!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="↩️ ᴍᴀɪɴ ᴍᴇɴᴜ", callback_data="menu:main")]
        ])
    )
    await cb.answer("✅ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴛɪᴠᴇ!")


# ═══════════════════════════════════════════════
# /premiumstatus
# ═══════════════════════════════════════════════
@router.message(F.text.regexp(r"^/premiumstatus(@\w+)?(\s|$)"))
@dm_only
async def cmd_premium_status(message: Message):
    await get_or_create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
    )

    if message.from_user.id in OWNER_IDS:
        return await message.reply(
            f"⭐ <b>ᴘʀᴇᴍɪᴜᴍ ꜱᴛᴀᴛᴜꜱ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👑 <b>ʙᴏᴛ ᴏᴡɴᴇʀ</b>\n\n"
            f"✅ ᴘʀᴇᴍɪᴜᴍ: <b>ᴜɴʟɪᴍɪᴛᴇᴅ</b>\n"
            f"♾️ ᴇxᴘɪʀᴇꜱ: <b>ɴᴇᴠᴇʀ</b>\n\n"
            f"🎁 ᴇɴᴊᴏʏ ᴀʟʟ ᴏᴡɴᴇʀ ʙᴇɴᴇꜰɪᴛꜱ ꜰᴏʀᴇᴠᴇʀ!"
        )

    is_active, expires_at, days_left = await get_premium_status(message.from_user.id)

    if not is_active:
        return await message.reply(
            f"⭐ <b>ᴘʀᴇᴍɪᴜᴍ ꜱᴛᴀᴛᴜꜱ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"❌ ᴀᴀᴘᴋᴇ ᴀᴄᴄᴏᴜɴᴛ ᴘᴀʀ ᴀʙʜɪ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴛɪᴠᴇ ɴᴀʜɪ ʜᴀɪ.\n\n"
            f"💫 ᴜꜱᴇ /premium ᴛᴏ ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ."
        )

    try:
        dt = datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
        expiry_str = dt.strftime("%d %b %Y, %H:%M UTC")
    except Exception:
        expiry_str = expires_at

    await message.reply(
        f"⭐ <b>ᴘʀᴇᴍɪᴜᴍ ꜱᴛᴀᴛᴜꜱ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"✅ ᴘʀᴇᴍɪᴜᴍ: <b>ᴀᴄᴛɪᴠᴇ</b>\n"
        f"📅 ᴇxᴘɪʀᴇꜱ: <b>{expiry_str}</b>\n"
        f"⏳ ᴅᴀʏꜱ ʟᴇꜰᴛ: <b>{days_left}</b>\n\n"
        f"🎁 ᴇɴᴊᴏʏ ʏᴏᴜʀ ʙᴇɴᴇꜰɪᴛꜱ!"
    )


# ═══════════════════════════════════════════════
# 🎨 /setemoji — Premium custom emoji
# ═══════════════════════════════════════════════
@router.message(F.text.regexp(r"^/setemoji(@\w+)?(\s|$)"))
@dm_only
async def cmd_setemoji(message: Message):
    await get_or_create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
    )

    # ═══ Premium check ═══
    is_active = False
    if message.from_user.id in OWNER_IDS:
        is_active = True
    else:
        status, _, _ = await get_premium_status(message.from_user.id)
        is_active = status

    if not is_active:
        return await message.reply(
            f"❌ <b>ᴘʀᴇᴍɪᴜᴍ ᴏɴʟʏ</b>\n\n"
            f"ᴄᴜꜱᴛᴏᴍ ᴇᴍᴏᴊɪ ɪꜱ ᴀ ᴘʀᴇᴍɪᴜᴍ ꜰᴇᴀᴛᴜʀᴇ.\n\n"
            f"💫 ᴜꜱᴇ /premium ᴛᴏ ɢᴇᴛ ᴘʀᴇᴍɪᴜᴍ."
        )

    # ═══ Parse argument ═══
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        current = await get_custom_emoji(message.from_user.id)
        return await message.reply(
            f"🎨 <b>ꜱᴇᴛ ᴄᴜꜱᴛᴏᴍ ᴇᴍᴏᴊɪ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"ᴜꜱᴀɢᴇ: <code>/setemoji 🚀</code>\n\n"
            f"ᴄᴜʀʀᴇɴᴛ: {current or 'ησηє'}\n\n"
            f"ᴛʜɪꜱ ᴇᴍᴏᴊɪ ᴡɪʟʟ ꜱʜᴏᴡ ᴜᴘ ɪɴ ꜰʀᴏɴᴛ ᴏꜰ ʏᴏᴜʀ\n"
            f"ᴜꜱᴇʀɴᴀᴍᴇ ᴏɴ ᴀʟʟ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅꜱ! 🏆"
        )

    emoji = parts[1].strip()

    # ═══ Validate ═══
    if len(emoji) > 5:
        return await message.reply(
            "❌ ᴇᴍᴏᴊɪ ᴛᴏᴏ ʟᴏɴɢ! ᴍᴀx 5 ᴄʜᴀʀᴀᴄᴛᴇʀꜱ ᴏɴʟʏ."
        )

    # ═══ Save ═══
    await set_custom_emoji(message.from_user.id, emoji)

    await message.reply(
        f"✅ <b>ᴄᴜꜱᴛᴏᴍ ᴇᴍᴏᴊɪ ꜱᴀᴠᴇᴅ!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ʏᴏᴜʀ ᴇᴍᴏᴊɪ: <b>{emoji}</b>\n\n"
        f"ɪᴛ ᴡɪʟʟ ᴀᴘᴘᴇᴀʀ ʙᴇꜰᴏʀᴇ ʏᴏᴜʀ ɴᴀᴍᴇ ɪɴ ᴀʟʟ\n"
        f"ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅꜱ! 🏆\n\n"
        f"📌 ᴛᴏ ʀᴇᴍᴏᴠᴇ: <code>/setemoji ∅</code>"
    )
