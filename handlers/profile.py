from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import XP_PER_LEVEL_BASE, MAX_LEVEL
from utils.database import (
    get_or_create_user, get_user_by_astral_id, get_user_by_username,
    get_user_by_id, convert_coins_to_gems, is_premium,
    get_user_coins, get_user_gems, get_extra_plays,
    compute_level_from_xp, compute_level_progress, get_level_title,
    progress_bar,
)

router = Router()


# ═══════════════════════════════════════════════
# FORMAT PROFILE
# ═══════════════════════════════════════════════
async def format_balance(u, premium: bool = False) -> str:
    name = u["first_name"] or "ᴜɴᴋɴᴏᴡɴ"
    uname = f"@{u['username']}" if u["username"] else "ɴᴏɴᴇ"
    astral_id = u["astral_id"] or "—"
    coins = u["coins"] or 0
    gems = u["gems"] or 0
    total_xp = u["xp"] or 0
    quiz_solved = u["quiz_solved"] or 0

    # Level math
    level = compute_level_from_xp(total_xp)
    xp_in_level, xp_needed = compute_level_progress(total_xp, level)
    bar = progress_bar(xp_in_level, xp_needed)
    title = get_level_title(level)
    extras = await get_extra_plays(u["user_id"])

    # ═══ Owner check ═══
    try:
        from config import OWNER_IDS
        is_owner = u["user_id"] in OWNER_IDS
    except Exception:
        is_owner = False

    if is_owner:
        header = "👑 <b>ᴏᴡɴᴇʀ ᴘʀᴏꜰɪʟᴇ</b> 👑"
    elif premium:
        header = "💎 <b>ᴘʀᴇᴍɪᴜᴍ ᴘʀᴏꜰɪʟᴇ</b> 💎"
    else:
        header = "👤 <b>ʙᴀʟᴀɴᴄᴇ</b>"

    # ═══ Level line ═══
    if level >= MAX_LEVEL:
        level_line = (
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"⭐ ʟᴇᴠᴇʟ: <b>{level}</b> / {MAX_LEVEL}  •  👑 {title}\n"
            f"♾️ <b>ᴍᴀx ʟᴇᴠᴇʟ ʀᴇᴀᴄʜᴇᴅ</b>\n"
            f"<code>{'▰' * 10}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━"
        )
    else:
        level_line = (
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"⭐ ʟᴇᴠᴇʟ: <b>{level}</b>  •  👑 {title}\n"
            f"⚡ xᴘ: <b>{xp_in_level:,} / {xp_needed:,}</b>\n"
            f"<code>{bar}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━"
        )

    return (
        f"{header}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"✨ ɴᴀᴍᴇ       — <b>{name}</b>\n"
        f"😄 ᴜꜱᴇʀɴᴀᴍᴇ  — {uname}\n"
        f"🚀 ᴀꜱᴛʀᴀʟ ɪᴅ — <code>{astral_id}</code>\n\n"
        f"🪙 ᴄᴏɪɴꜱ       — <b>{coins:,}</b>\n"
        f"📈 xᴘ          — <b>{total_xp:,}</b>\n"
        f"🧠 ǫᴜɪᴢ ꜱᴏʟᴠᴇᴅ — <b>{quiz_solved}</b>\n"
        f"💎 ɢᴇᴍꜱ         — <b>{gems:,}</b>\n"
        f"🎟️ ᴇxᴛʀᴀ ᴘʟᴀʏꜱ — <b>{extras}</b>\n\n"
        f"{level_line}"
    )


# ═══════════════════════════════════════════════
# /balance — DM + GC
# ═══════════════════════════════════════════════
@router.message(Command("balance"))
async def cmd_balance(message: Message):
    # Priority 1: Reply
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
        await get_or_create_user(target.id, target.username, target.first_name)
        u = await get_user_by_id(target.id)
        if not u:
            return await message.reply("❌ ᴜꜱᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ.")
        prem = await is_premium(target.id)
        return await message.reply(await format_balance(u, prem))

    # Priority 2: Args
    parts = (message.text or "").split()
    args = parts[1:] if len(parts) > 1 else []

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
        return await message.reply(await format_balance(u, prem))

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
    await message.reply(await format_balance(u, prem))


# Alias
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
            "❌ ɪɴꜱᴜꜰꜰɪᴄɪᴇɴᴛ ᴄᴏɪɴꜱ!\n\nʏᴏᴜ ɴᴇᴇᴅ 100 🪙 ᴛᴏ ᴄᴏɴᴠᴇʀᴛ ᴛᴏ 1 💎."
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
                "❌ ɪɴꜱᴜꜰꜰɪᴄɪᴇɴᴛ ᴄᴏɪɴꜱ!\n\nʏᴏᴜ ɴᴇᴇᴅ 100 🪙 ᴛᴏ ᴄᴏɴᴠᴇʀᴛ ᴛᴏ 1 💎."
            )
        return await message.reply("❌ ᴄᴏɴᴠᴇʀꜱɪᴏɴ ꜰᴀɪʟᴇᴅ.")

    coins = await get_user_coins(message.from_user.id)
    gems = await get_user_gems(message.from_user.id)

    await message.reply(
        f"✅ <b>ᴄᴏɴᴠᴇʀꜱɪᴏɴ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ!</b>\n\n"
        f"🪙 -{result * 100} ᴄᴏɪɴꜱ\n"
        f"💎 +{result} ɢᴇᴍ\n\n"
        f"🪙 ᴄᴏɪɴꜱ: <b>{coins:,}</b>\n"
        f"💎 ɢᴇᴍꜱ: <b>{gems:,}</b>"
    )
