from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import XP_PER_LEVEL_BASE, LEVEL_TITLES
from utils.database import (
    get_or_create_user, get_user_by_astral_id, get_user_by_username,
    get_user_by_id, convert_coins_to_gems, is_premium,
    get_user_coins, get_user_gems, get_extra_plays,
)

router = Router()


# ═══════════════════════════════════════════════
# LEVEL MATH HELPERS
# ═══════════════════════════════════════════════
def _cumulative_xp_for_level(level: int) -> int:
    """Total lifetime XP needed to REACH the given level."""
    if level <= 1:
        return 0
    return XP_PER_LEVEL_BASE * (level - 1) * level // 2


def _compute_level_from_xp(total_xp: int) -> int:
    """Given lifetime total XP, return current level."""
    if total_xp < 0:
        total_xp = 0
    level = 1
    while _cumulative_xp_for_level(level + 1) <= total_xp:
        level += 1
        if level > 9999:
            break
    return level


def _compute_level_progress(total_xp: int, level: int):
    """Return (xp_in_current_level, xp_needed_for_next)."""
    current_threshold = _cumulative_xp_for_level(level)
    xp_in_level = total_xp - current_threshold
    xp_needed = level * XP_PER_LEVEL_BASE
    if xp_in_level < 0:
        xp_in_level = 0
    return xp_in_level, xp_needed


def _progress_bar(current: int, needed: int, length: int = 10) -> str:
    if needed <= 0:
        return "▰" * length
    filled = int((current / needed) * length)
    filled = max(0, min(length, filled))
    return "▰" * filled + "░" * (length - filled)


def _get_level_title(level: int) -> str:
    for lvl, title in LEVEL_TITLES:
        if level >= lvl:
            return title
    return "Astral Rookie"


# ═══════════════════════════════════════════════
# FORMAT PROFILE / BALANCE
# ═══════════════════════════════════════════════
async def format_balance(u, premium: bool = False) -> str:
    name = u["first_name"] or "ᴜɴᴋɴᴏᴡɴ"
    uname = f"@{u['username']}" if u["username"] else "ɴᴏɴᴇ"
    astral_id = u["astral_id"] or "—"
    coins = u["coins"] or 0
    gems = u["gems"] or 0
    total_xp = u["xp"] or 0
    quiz_solved = u["quiz_solved"] or 0

    # ═══ Level math ═══
    level = _compute_level_from_xp(total_xp)
    xp_in_level, xp_needed = _compute_level_progress(total_xp, level)
    bar = _progress_bar(xp_in_level, xp_needed)
    title = _get_level_title(level)
    extras = await get_extra_plays(u["user_id"])

    header = "👑 <b>ᴘʀᴇᴍɪᴜᴍ ᴘʀᴏꜰɪʟᴇ</b> 👑" if premium else "👤 <b>ʙᴀʟᴀɴᴄᴇ</b>"

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
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"⭐ ʟᴇᴠᴇʟ: <b>{level}</b>  •  👑 {title}\n"
        f"⚡ xᴘ: <b>{xp_in_level:,} / {xp_needed:,}</b>\n"
        f"<code>{bar}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━"
    )


# ═══════════════════════════════════════════════
# /balance — DM + GC
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
        return await message.reply(await format_balance(u, prem))

    # ═══ Priority 2: Args ═══
    parts = (message.text or "").split()
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
        return await message.reply(await format_balance(u, prem))

    # Has arg
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


# ═══ Alias: /profile → /balance ═══
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
