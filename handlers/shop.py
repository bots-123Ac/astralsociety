from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from keyboards.main_menu import shop_kb, xpboost_kb, back_main_kb
from utils.database import (
    get_or_create_user, add_gems, add_power,
    shield_remaining_seconds, format_shield_time,
    get_user_by_astral_id, get_user_by_id, get_user_by_username,
    get_pool,
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
        f"👁️ <b>ᴩʀσᴛєᴄтiση ᴄнєᴄᴋєʀ ᴩᴜʀᴄнᴧsєᴅ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"✅ ᴩᴜʀᴄнᴧsєᴅ!\n"
        f"💎 -6 ɢєᴍs\n\n"
        f"ᴜsє <code>/shieldtime &lt;ᴜsєʀ_iᴅ&gt;</code> ᴛσ ᴄнєᴄᴋ sнiєʟᴅ тiϻє.",
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


# ═══════════════════════════════════════════════
# /shieldtime — 4 WAYS TO LOOKUP
# 1. Reply to user
# 2. @username
# 3. 6-digit Astral ID
# 4. Telegram user_id
# ═══════════════════════════════════════════════
@router.message(F.text.regexp(r"^/shieldtime(\s|$)"))
async def cmd_shieldtime(message: Message):
    target_id = None
    display = ""

    # ═══ Method 1: Reply to user ═══
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
        target_id = target.id
        display = target.mention_html()

    else:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            return await message.reply(
                "ᴜsᴇʀsɪᴅ ᴩʀσᴠiᴅє ᴋᴧʀσ!\n\n"
                "<b>ᴜsᴧɢє:</b>\n"
                "• <code>/shieldtime 7790607144</code> (ᴛєʟєɢʀᴧϻ ɪᴅ)\n"
                "• <code>/shieldtime 954974</code> (ᴧsᴛʀᴧʟ ɪᴅ)\n"
                "• <code>/shieldtime @username</code>\n"
                "• ʏᴧ ᴜsєʀ ᴋє ϻєssᴧɢє ᴩє ʀєᴩʟʏ ᴋᴧʀσ"
            )

        arg = parts[1].strip()

        # ═══ Method 2: @username ═══
        if arg.startswith("@"):
            u = await get_user_by_username(arg)
            if not u:
                return await message.reply(f"❌ ᴜsєʀ <b>{arg}</b> ησт ғσᴜηᴅ.")
            target_id = u["user_id"]
            display = f"@{u['username']}" if u["username"] else u["first_name"]

        # ═══ Method 3 & 4: Numeric (6-digit = Astral, else Telegram) ═══
        elif arg.isdigit():
            num = int(arg)
            if len(arg) == 6:
                # Try Astral ID first
                u = await get_user_by_astral_id(arg)
                if u:
                    target_id = u["user_id"]
                    display = u["first_name"] or f"ID {arg}"
                else:
                    return await message.reply(f"❌ ᴧsᴛʀᴧʟ ɪᴅ <code>{arg}</code> ησт ғσᴜηᴅ.")
            else:
                # Assume Telegram user_id
                u = await get_user_by_id(num)
                if u:
                    target_id = num
                    display = u["first_name"] or f"ID {num}"
                else:
                    return await message.reply(f"❌ ᴜsєʀ <code>{num}</code> ησт ғσᴜηᴅ.")

        else:
            return await message.reply("❌ iηᴠᴧʟiᴅ ϻєтнσᴅ.")

    if not target_id:
        return await message.reply("❌ ᴜsєʀ ησт ғσᴜηᴅ.")

    # ═══ Fetch shield time in SECONDS ═══
    rem_seconds = await shield_remaining_seconds(target_id)

    if rem_seconds <= 0:
        return await message.reply(
            f"❌ ᴜsєʀ <b>{display}</b> нᴧs ησ ᴧᴄтiᴠє sнiєʟᴅ."
        )

    await message.reply(
        f"🛡️ <b>sнiєʟᴅ sтᴧтᴜs</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 ᴜsєʀ: <b>{display}</b>\n"
        f"⏳ ʀєϻᴧiηiηɢ: <b>{format_shield_time(rem_seconds)}</b>"
    )
