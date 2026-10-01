import random
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from keyboards.main_menu import (
    shop_kb, xpboost_kb, protection_kb, back_main_kb,
)
from config import (
    PROTECTION_CHECKER_PLANS, XP_BOOST_PLANS,
    EXTRA_PLAY_PRICE, MYSTERY_CHEST_PRICE, MYSTERY_CHEST_REWARDS,
)
from utils.database import (
    get_or_create_user, add_gems, add_power, add_coins, add_xp,
    add_extra_play, shield_remaining, get_pool,
)
from utils.checks import dm_only
from utils.xp import format_level_up_message

router = Router()


# ═══════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════
async def _get_gems(user_id) -> int:
    pool = await get_pool()
    val = await pool.fetchval("SELECT gems FROM users WHERE user_id = $1", user_id)
    return val or 0


# ═══════════════════════════════════════════════
# /shop
# ═══════════════════════════════════════════════
@router.message(F.text.regexp(r"^/shop(@\w+)?(\s|$)"))
@dm_only
async def cmd_shop(message: Message):
    await get_or_create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
    )
    await message.answer(
        f"🛒 <b>ᴀꜱᴛʀᴀʟ ꜱʜᴏᴘ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\nᴄʜᴏᴏꜱᴇ ᴀɴ ɪᴛᴇᴍ:",
        reply_markup=shop_kb()
    )


@router.callback_query(F.data == "shop:back")
async def shop_back(cb: CallbackQuery):
    await cb.message.edit_text(
        f"🛒 <b>ᴀꜱᴛʀᴀʟ ꜱʜᴏᴘ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\nᴄʜᴏᴏꜱᴇ ᴀɴ ɪᴛᴇᴍ:",
        reply_markup=shop_kb()
    )
    await cb.answer()


# ═══════════════════════════════════════════════
# 🛡️ PROTECTION CHECKER
# ═══════════════════════════════════════════════
@router.callback_query(F.data == "shop:protection")
async def shop_protection(cb: CallbackQuery):
    await cb.message.edit_text(
        f"🛡️ <b>ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ᴄʜᴇᴄᴋᴇʀ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ᴀʟʟᴏᴡꜱ ʏᴏᴜ ᴛᴏ ᴄʜᴇᴄᴋ ᴏᴛʜᴇʀ ᴜꜱᴇʀꜱ' ꜱʜɪᴇʟᴅ ᴛɪᴍᴇ.\n\n"
        f"ᴄʜᴏᴏꜱᴇ ᴀ ᴘʟᴀɴ:",
        reply_markup=protection_kb()
    )
    await cb.answer()


@router.callback_query(F.data.startswith("shop:pc:"))
async def shop_protection_buy(cb: CallbackQuery):
    plan_key = cb.data.split(":")[2]
    plan = PROTECTION_CHECKER_PLANS.get(plan_key)
    if not plan:
        return await cb.answer("ɪɴᴠᴀʟɪᴅ ᴘʟᴀɴ", show_alert=True)

    gems = await _get_gems(cb.from_user.id)
    if gems < plan["gems"]:
        return await cb.answer(
            f"❌ ɴᴇᴇᴅ {plan['gems']} 💎 ɢᴇᴍꜱ.\nʏᴏᴜ ʜᴀᴠᴇ: {gems} 💎",
            show_alert=True
        )

    await add_gems(cb.from_user.id, -plan["gems"])
    await add_power(cb.from_user.id, "protection_checker", plan["days"])

    await cb.message.edit_text(
        f"✅ <b>ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ᴄʜᴇᴄᴋᴇʀ ᴀᴄᴛɪᴠᴀᴛᴇᴅ!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🛡️ ᴘʟᴀɴ: <b>{plan['label']}</b>\n"
        f"💎 ᴘᴀɪᴅ: <b>{plan['gems']} ɢᴇᴍꜱ</b>\n\n"
        f"ɴᴏᴡ ʏᴏᴜ ᴄᴀɴ ᴜꜱᴇ <code>/shieldcheck @user</code>!",
        reply_markup=back_main_kb()
    )
    await cb.answer("✅")


# ═══════════════════════════════════════════════
# ⚡ XP BOOST
# ═══════════════════════════════════════════════
@router.callback_query(F.data == "shop:xpboost")
async def shop_xpboost(cb: CallbackQuery):
    await cb.message.edit_text(
        f"⚡ <b>xᴘ ʙᴏᴏꜱᴛ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ɢᴇᴛ <b>2× xᴘ</b> ꜰʀᴏᴍ ᴀʟʟ ɢᴀᴍᴇꜱ!\n\n"
        f"ᴄʜᴏᴏꜱᴇ ᴀ ᴘʟᴀɴ:",
        reply_markup=xpboost_kb()
    )
    await cb.answer()


@router.callback_query(F.data.startswith("shop:xp:"))
async def shop_xp_buy(cb: CallbackQuery):
    plan_key = cb.data.split(":")[2]
    plan = XP_BOOST_PLANS.get(plan_key)
    if not plan:
        return await cb.answer("ɪɴᴠᴀʟɪᴅ ᴘʟᴀɴ", show_alert=True)

    gems = await _get_gems(cb.from_user.id)
    if gems < plan["gems"]:
        return await cb.answer(
            f"❌ ɴᴇᴇᴅ {plan['gems']} 💎 ɢᴇᴍꜱ.\nʏᴏᴜ ʜᴀᴠᴇ: {gems} 💎",
            show_alert=True
        )

    await add_gems(cb.from_user.id, -plan["gems"])
    await add_power(cb.from_user.id, "xp_boost", plan["days"])

    await cb.message.edit_text(
        f"✅ <b>xᴘ ʙᴏᴏꜱᴛ ᴀᴄᴛɪᴠᴀᴛᴇᴅ!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⚡ ᴘʟᴀɴ: <b>{plan['label']}</b>\n"
        f"💎 ᴘᴀɪᴅ: <b>{plan['gems']} ɢᴇᴍꜱ</b>\n\n"
        f"ᴇɴᴊᴏʏ <b>2× xᴘ</b> ꜰʀᴏᴍ ɢᴀᴍᴇꜱ!",
        reply_markup=back_main_kb()
    )
    await cb.answer("✅")


# ═══════════════════════════════════════════════
# 🎟️ EXTRA PLAY
# ═══════════════════════════════════════════════
@router.callback_query(F.data == "shop:extraplay")
async def shop_extraplay(cb: CallbackQuery):
    gems = await _get_gems(cb.from_user.id)
    if gems < EXTRA_PLAY_PRICE:
        return await cb.answer(
            f"❌ ɴᴇᴇᴅ {EXTRA_PLAY_PRICE} 💎 ɢᴇᴍꜱ.\nʏᴏᴜ ʜᴀᴠᴇ: {gems} 💎",
            show_alert=True
        )

    await add_gems(cb.from_user.id, -EXTRA_PLAY_PRICE)
    await add_extra_play(cb.from_user.id, 1)

    from utils.database import get_extra_plays
    total = await get_extra_plays(cb.from_user.id)

    await cb.message.edit_text(
        f"✅ <b>ᴇxᴛʀᴀ ᴘʟᴀʏ ᴘᴜʀᴄʜᴀꜱᴇᴅ!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎟️ +1 ᴇxᴛʀᴀ ᴘʟᴀʏ\n"
        f"💎 ᴘᴀɪᴅ: <b>{EXTRA_PLAY_PRICE} ɢᴇᴍꜱ</b>\n\n"
        f"📦 ʏᴏᴜʀ ᴛᴏᴛᴀʟ ᴇxᴛʀᴀ ᴘʟᴀʏꜱ: <b>{total}</b>",
        reply_markup=back_main_kb()
    )
    await cb.answer("✅")


# ═══════════════════════════════════════════════
# 🔮 MYSTERY CHEST
# ═══════════════════════════════════════════════
@router.callback_query(F.data == "shop:mystery")
async def shop_mystery(cb: CallbackQuery):
    gems = await _get_gems(cb.from_user.id)
    if gems < MYSTERY_CHEST_PRICE:
        return await cb.answer(
            f"❌ ɴᴇᴇᴅ {MYSTERY_CHEST_PRICE} 💎 ɢᴇᴍꜱ.\nʏᴏᴜ ʜᴀᴠᴇ: {gems} 💎",
            show_alert=True
        )

    await add_gems(cb.from_user.id, -MYSTERY_CHEST_PRICE)

    # Weighted random pick
    rewards = MYSTERY_CHEST_REWARDS
    weights = [r["weight"] for r in rewards]
    reward = random.choices(rewards, weights=weights, k=1)[0]

    xp_info = None
    rtype = reward["type"]

    if rtype == "coins":
        await add_coins(cb.from_user.id, reward["amount"])
    elif rtype == "gems":
        await add_gems(cb.from_user.id, reward["amount"])
    elif rtype == "xp":
        xp_info = await add_xp(cb.from_user.id, reward["amount"])
    elif rtype == "xp_boost":
        await add_power(cb.from_user.id, "xp_boost", reward["days"])
    elif rtype == "extra_play":
        await add_extra_play(cb.from_user.id, reward["amount"])

    await cb.message.edit_text(
        f"🔮 <b>ᴍʏꜱᴛᴇʀʏ ᴄʜᴇꜱᴛ ᴏᴘᴇɴᴇᴅ!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎉 ʏᴏᴜ ʀᴇᴄᴇɪᴠᴇᴅ:\n"
        f"<b>{reward['label']}</b>\n\n"
        f"💎 ᴘᴀɪᴅ: <b>{MYSTERY_CHEST_PRICE} ɢᴇᴍꜱ</b>",
        reply_markup=back_main_kb()
    )

    if xp_info:
        try:
            await cb.message.answer(format_level_up_message(xp_info))
        except Exception:
            pass

    await cb.answer("🎉")


# ═══════════════════════════════════════════════
# /shieldtime (unchanged)
# ═══════════════════════════════════════════════
@router.message(F.text.regexp(r"^/shieldtime(\s|$)"))
async def cmd_shieldtime(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip().isdigit():
        return await message.reply("ᴜꜱᴀɢᴇ: <code>/shieldtime &lt;ᴜꜱᴇʀ_iᴅ&gt;</code>")
    uid = int(parts[1].strip())
    rem = await shield_remaining(uid)
    if rem <= 0:
        return await message.reply(f"❌ ᴜꜱᴇʀ <code>{uid}</code> ʜᴀꜱ ɴᴏ ᴀᴄᴛɪᴠᴇ ꜱʜɪᴇʟᴅ.")
    await message.reply(f"🛡️ ᴜꜱᴇʀ <code>{uid}</code>: <b>{rem} ᴅᴀʏꜱ ʟᴇꜰᴛ</b>.")
