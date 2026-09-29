from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

from config import PREMIUM_PLANS
from utils.database import (
    get_or_create_user, get_premium_status, deduct_gems, set_premium, get_pool,
)
from utils.checks import dm_only

router = Router()


def premium_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 ᴡᴇᴇᴋ — 1,000 💎", callback_data="prem_buy:1w")],
        [InlineKeyboardButton(text="1 ᴍᴏɴᴛʜ — 10,000 💎", callback_data="prem_buy:1m")],
        [InlineKeyboardButton(text="1 ʏᴇᴀʀ — 100,000 💎", callback_data="prem_buy:1y")],
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
        f"• ᴘʀᴇᴍɪᴜᴍ ᴘʀᴏꜰɪʟᴇ ꜱᴛʏʟᴇ\n"
        f"• 🔍 <b>/shieldcheck</b> ᴛᴏ ᴄʜᴇᴄᴋ ᴏᴛʜᴇʀꜱ' ꜱʜɪᴇʟᴅ\n\n"
        f"💫 ᴄʜᴏᴏꜱᴇ ᴀ ᴘʟᴀɴ:"
    )


@router.message(F.text.regexp(r"^/premium(@\w+)?(\s|$)"))
@dm_only
async def cmd_premium(message: Message):
    await get_or_create_user(
        message.from_user.id, message.from_user.username, message.from_user.first_name
    )
    await message.answer(premium_main_text(), reply_markup=premium_menu_kb())


@router.callback_query(F.data.startswith("prem_buy:"))
async def cb_prem_buy(cb: CallbackQuery):
    plan_key = cb.data.split(":")[1]
    plan = PREMIUM_PLANS.get(plan_key)
    if not plan:
        return await cb.answer("ɪɴᴠᴀʟɪᴅ ᴘʟᴀɴ.", show_alert=True)

    user_id = cb.from_user.id

    is_active, expires_at, days_left = await get_premium_status(user_id)
    if is_active:
        return await cb.answer(
            f"⚠️ ʏᴏᴜ ᴀʀᴇ ᴀʟʀᴇᴀᴅʏ ᴘʀᴇᴍɪᴜᴍ!\nᴇxᴘɪʀᴇꜱ ɪɴ {days_left} ᴅᴀʏꜱ.",
            show_alert=True
        )

    pool = await get_pool()
    current_gems = await pool.fetchval("SELECT gems FROM users WHERE user_id = $1", user_id)
    current_gems = current_gems or 0

    if current_gems < plan["gems"]:
        return await cb.answer(
            f"❌ ɪɴꜱᴜꜰꜰɪᴄɪᴇɴᴛ ɢᴇᴍꜱ!\n\nʏᴏᴜ ʜᴀᴠᴇ: {current_gems:,} 💎\nɴᴇᴇᴅ: {plan['gems']:,} 💎",
            show_alert=True
        )

    ok = await deduct_gems(user_id, plan["gems"])
    if not ok:
        return await cb.answer("❌ ʟᴏꜱᴛ ɢᴇᴍꜱ ɪɴ ᴛʀᴀɴꜱᴀᴄᴛɪᴏɴ.", show_alert=True)

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


@router.message(F.text.regexp(r"^/premiumstatus(@\w+)?(\s|$)"))
@dm_only
async def cmd_premium_status(message: Message):
    await get_or_create_user(
        message.from_user.id, message.from_user.username, message.from_user.first_name
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
