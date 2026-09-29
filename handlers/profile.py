from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from utils.database import (
    get_or_create_user, get_user_by_astral_id, get_user_by_username,
    get_user_by_id, convert_coins_to_gems, is_premium,
    get_user_coins, get_user_gems,
)

router = Router()


def format_balance(u, premium: bool = False) -> str:
    name = u["first_name"] or "ᴜɴᴋɴᴏᴡɴ"
    uname = f"@{u['username']}" if u["username"] else "ɴᴏɴᴇ"
    astral_id = u["astral_id"] or "—"
    coins = u["coins"] or 0
    gems = u["gems"] or 0
    xp = u["xp"] or 0
    quiz_solved = u["quiz_solved"] or 0

    if premium:
        return (
            f"👑 <b>ᴘʀᴇᴍɪᴜᴍ ᴘʀᴏꜰɪʟᴇ</b> 👑\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"⭐ <b>ᴘʀᴇᴍɪᴜᴍ ᴍᴇᴍʙᴇʀ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"✨ ɴᴀᴍᴇ       — <b>{name}</b>\n"
            f"😄 ᴜꜱᴇʀɴᴀᴍᴇ  — {uname}\n"
            f"🚀 ᴀꜱᴛʀᴀʟ ɪᴅ — <code>{astral_id}</code>\n\n"
            f"🪙 ᴄᴏɪɴꜱ       — <b>{coins:,}</b>\n"
            f"💎 ɢᴇᴍꜱ         — <b>{gems:,}</b>\n"
            f"📈 xᴘ          — <b>{xp:,}</b>\n"
            f"🧠 ǫᴜɪᴢ ꜱᴏʟᴠᴇᴅ — <b>{quiz_solved}</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"⭐ ᴘʀᴇᴍɪᴜᴍ ᴘᴇʀᴋꜱ ᴀᴄᴛɪᴠᴇ\n"
            f"━━━━━━━━━━━━━━━━━━━━━"
        )

    return (
        f"👤 <b>ʙᴀʟᴀɴᴄᴇ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"✨ ɴᴀᴍᴇ       — <b>{name}</b>\n"
        f"😄 ᴜꜱᴇʀɴᴀᴍᴇ  — {uname}\n"
        f"🚀 ᴀꜱᴛʀᴀʟ ɪᴅ — <code>{astral_id}</code>\n\n"
        f"🪙 ᴄᴏɪɴꜱ       — <b>{coins:,}</b>\n"
        f"📈 xᴘ          — <b>{xp:,}</b>\n"
        f"🧠 ǫᴜɪᴢ ꜱᴏʟᴠᴇᴅ — <b>{quiz_solved}</b>\n"
        f"💎 ɢᴇᴍꜱ         — <b>{gems:,}</b>"
    )


# ═══════════════════════════════════════════════
# /balance — DM + GC (reply / @username / ID / self)
# ═══════════════════════════════════════════════
@router.message(Command("balance"))
async def cmd_balance(message: Message):
    # ═══ Priority 1: Reply to a user ═══
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
        await get_or_create_user(target.id, target.username, target.first_name)
        u = await get_user_by_id(target.id)
        if not u:
            return await message.reply("❌ ᴜꜱᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ.")
        prem = await is_premium(target.id)
        return await message.reply(format_balance(u, prem))

    # ═══ Priority 2: Args ═══
    text = message.text or ""
    parts = text.split()
    args = parts[1:] if len(parts) > 1 else []

    # No args — own balance
    if not args:
        await get_or_create_user(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
        )
        u = await get_user_by_id(message.from_user.id)
        if not u:
            return await message.reply("❌ ᴜꜱᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ.")
        prem = await is_premium(message.from_user.id)
        return await message.reply(format_balance(u, prem))

    arg = args[0].strip()
    u = None

    if arg.startswith("@"):
        u = await get_user_by_username(arg)
    elif arg.isdigit():
        if len(arg) == 6:
            u = await get_user_by_astral_id(arg)
        if not u:
            u = await get_user_by_id(int(arg))
    else:
        u = await get_user_by_username(arg)

    if not u:
        return await message.reply("❌ ᴜꜱᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ.")
    prem = await is_premium(u["user_id"])
    await message.reply(format_balance(u, prem))


# ═══════════════════════════════════════════════
# ALIAS: /profile → /balance (still works)
# ═══════════════════════════════════════════════
@router.message(Command("profile"))
async def cmd_profile_alias(message: Message):
    await cmd_balance(message)


# ═══════════════════════════════════════════════
# /convert
# ═══════════════════════════════════════════════
@router.message(Command("convert"))
async def cmd_convert(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return await message.reply("ᴜꜱᴀɢᴇ: <code>/convert 100c</code>\n100 ᴄᴏɪɴꜱ = 1 ɢᴇᴍ")

    arg = parts[1].strip().lower().replace("c", "").replace(" ", "")
    if not arg.isdigit():
        return await message.reply("❌ ɪɴᴠᴀʟɪᴅ ᴀᴍᴏᴜɴᴛ.")

    amount = int(arg)
    if amount < 100:
        return await message.reply(
            "❌ ɪɴꜱᴜꜰꜰɪᴄɪᴇɴᴛ ᴄᴏɪɴꜱ!\n\n"
            "ʏᴏᴜ ɴᴇᴇᴅ 100 🪙 ᴄᴏɪɴꜱ ᴛᴏ ᴄᴏɴᴠᴇʀᴛ ᴛᴏ 1 💎 ɢᴇᴍ."
        )

    await get_or_create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
    )

    ok, result = await convert_coins_to_gems(message.from_user.id, amount)
    if not ok:
        if result == "insufficient":
            return await message.reply(
                "❌ ɪɴꜱᴜꜰꜰɪᴄɪᴇɴᴛ ᴄᴏɪɴꜱ!\n\n"
                "ʏᴏᴜ ɴᴇᴇᴅ 100 🪙 ᴄᴏɪɴꜱ ᴛᴏ ᴄᴏɴᴠᴇʀᴛ ᴛᴏ 1 💎 ɢᴇᴍ."
            )
        return await message.reply("❌ ᴄᴏɴᴠᴇʀꜱɪᴏɴ ꜰᴀɪʟᴇᴅ.")

    coins = await get_user_coins(message.from_user.id)
    gems = await get_user_gems(message.from_user.id)

    await message.reply(
        f"✅ <b>ᴄᴏɴᴠᴇʀꜱɪᴏɴ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ!</b>\n\n"
        f"🪙 -{result * 100} ᴄᴏɪɴꜱ\n"
        f"💎 +{result} ɢᴇᴍ\n\n"
        f"ʏᴏᴜʀ ʙᴀʟᴀɴᴄᴇ:\n"
        f"🪙 ᴄᴏɪɴꜱ: <b>{coins:,}</b>\n"
        f"💎 ɢᴇᴍꜱ:  <b>{gems:,}</b>"
    )
