from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from keyboards.main_menu import shop_kb, xpboost_kb, back_main_kb
from utils.database import (
    get_or_create_user, add_gems, add_power, shield_remaining, get_pool,
)
from utils.checks import dm_only

router = Router()


@router.message(F.text.regexp(r"^/shop(@\w+)?(\s|$)"))
@dm_only
async def cmd_shop(message: Message):
    await get_or_create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
    )
    await message.answer(
        f"🛒 <b>ᴧsᴛʀᴧʟ sнσᴩ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ᴄнσσsє ᴧη iтєϻ:",
        reply_markup=shop_kb()
    )


@router.callback_query(F.data == "shop:back")
async def shop_back(cb: CallbackQuery):
    await cb.message.edit_text(
        f"🛒 <b>ᴧsᴛʀᴧʟ sнσᴩ</b>\n━━━━━━━━━━━━━━━━━━━━━\n\nᴄнσσsє ᴧη iтєϻ:",
        reply_markup=shop_kb()
    )
    await cb.answer()


@router.callback_query(F.data == "shop:checker")
async def shop_checker(cb: CallbackQuery):
    pool = await get_pool()
    gems = await pool.fetchval("SELECT gems FROM users WHERE user_id = $1", cb.from_user.id)
    gems = gems or 0
    if gems < 6:
        return await cb.answer("❌ ɴєєᴅ 6 💎 ɢєᴍs.", show_alert=True)
    await add_gems(cb.from_user.id, -6)
    await cb.message.edit_text(
        f"👁️ <b>ᴩʀσᴛєᴄтiση ᴄнєᴄᴋєʀ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"✅ ᴩᴜʀᴄнᴧsєᴅ!\n"
        f"💎 -6 ɢєᴍs\n\n"
        f"ᴜsє <code>/shieldtime &lt;ᴜsєʀ_iᴅ&gt;</code> тσ ᴄнєᴄᴋ.",
        reply_markup=back_main_kb()
    )
    await cb.answer("✅")


@router.callback_query(F.data == "shop:xpboost")
async def shop_xpboost(cb: CallbackQuery):
    await cb.message.edit_text(
        f"⚡ <b>xᴩ вσσsт</b>\n━━━━━━━━━━━━━━━━━━━━━\n\nᴄнσσsє ᴅᴜʀᴧтiση:",
        reply_markup=xpboost_kb()
    )
    await cb.answer()


@router.callback_query(F.data.startswith("shop:xp:"))
async def shop_xp_buy(cb: CallbackQuery):
    days = int(cb.data.split(":")[2])
    cost = {5: 6, 7: 8, 12: 13}.get(days, 6)

    pool = await get_pool()
    gems = await pool.fetchval("SELECT gems FROM users WHERE user_id = $1", cb.from_user.id)
    gems = gems or 0
    if gems < cost:
        return await cb.answer(f"❌ ɴєєᴅ {cost} 💎 ɢєᴍs.", show_alert=True)

    await add_gems(cb.from_user.id, -cost)
    await add_power(cb.from_user.id, "xp_boost", days)
    await cb.message.edit_text(
        f"⚡ <b>xᴩ вσσsт ᴧᴄтiᴠᴧтєᴅ!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ᴅᴜʀᴧтiση: <b>{days} ᴅᴧʏs</b>\n"
        f"💎 -{cost} ɢєᴍs\n\n"
        f"ησω ʏσᴜ ɢєт <b>2× xᴩ</b> ғʀσϻ ɢᴧϻєs!",
        reply_markup=back_main_kb()
    )
    await cb.answer("✅")


@router.message(F.text.regexp(r"^/shieldtime(\s|$)"))
async def cmd_shieldtime(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip().isdigit():
        return await message.reply("ᴜsᴧɢє: <code>/shieldtime &lt;ᴜsєʀ_iᴅ&gt;</code>")
    uid = int(parts[1].strip())
    rem = await shield_remaining(uid)
    if rem <= 0:
        return await message.reply(f"❌ ᴜsєʀ <code>{uid}</code> нᴧs ησ ᴧᴄтiᴠє sнiєʟᴅ.")
    await message.reply(f"🛡️ ᴜsєʀ <code>{uid}</code>: <b>{rem} ᴅᴧʏs ʟєғт</b>.")
