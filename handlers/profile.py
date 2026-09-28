from aiogram import Router, F
from aiogram.types import Message
import aiosqlite
from config import DB_PATH
from utils.database import (
    get_or_create_user, get_user_by_astral_id, get_user_by_username,
    convert_coins_to_gems, is_premium,
)

router = Router()


def format_profile(u, premium: bool = False) -> str:
    name = u[2] or "ᴜɴᴋɴᴏᴡɴ"
    uname = f"@{u[1]}" if u[1] else "ɴᴏɴᴇ"
    astral_id = u[3] or "—"
    coins = u[4] or 0
    gems = u[5] or 0
    xp = u[6] or 0
    quiz_solved = u[8] or 0

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
        f"👤 <b>ᴘʀᴏꜰɪʟᴇ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"✨ ɴᴀᴍᴇ       — <b>{name}</b>\n"
        f"😄 ᴜꜱᴇʀɴᴀᴍᴇ  — {uname}\n"
        f"🚀 ᴀꜱᴛʀᴀʟ ɪᴅ — <code>{astral_id}</code>\n\n"
        f"🪙 ᴄᴏɪɴꜱ       — <b>{coins:,}</b>\n"
        f"📈 xᴘ          — <b>{xp:,}</b>\n"
        f"🧠 ǫᴜɪᴢ ꜱᴏʟᴠᴇᴅ — <b>{quiz_solved}</b>\n"
        f"💎 ɢᴇᴍꜱ         — <b>{gems:,}</b>"
    )


async def _fetch_user_by_id(uid):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM users WHERE user_id=?", (uid,)) as cur:
            return await cur.fetchone()


@router.message(F.text.regexp(r"^/profile(\s|$)") | F.text.regexp(r"^/profile@\w+(\s|$)"))
async def cmd_profile(message: Message):
    # Reply to a user
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
        await get_or_create_user(target.id, target.username, target.first_name)
        u = await _fetch_user_by_id(target.id)
        if not u:
            return await message.reply("❌ ᴜꜱᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ.")
        prem = await is_premium(target.id)
        return await message.reply(format_profile(u, prem))

    # Args
    text = message.text or ""
    parts = text.split()
    args = parts[1:] if len(parts) > 1 else []

    if not args:
        await get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
        u = await _fetch_user_by_id(message.from_user.id)
        if not u:
            return await message.reply("❌ ᴜꜱᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ.")
        prem = await is_premium(message.from_user.id)
        return await message.reply(format_profile(u, prem))

    arg = args[0].strip()
    u = None
    if arg.startswith("@"):
        u = await get_user_by_username(arg)
    elif arg.isdigit():
        if len(arg) == 6:
            u = await get_user_by_astral_id(arg)
        if not u:
            u = await _fetch_user_by_id(int(arg))
    else:
        u = await get_user_by_username(arg)

    if not u:
        return await message.reply("❌ ᴜꜱᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ.")
    prem = await is_premium(u[0])
    await message.reply(format_profile(u, prem))


# ═══ /convert ═══
@router.message(F.text.regexp(r"^/convert(\s|$)"))
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
            "❌ ɪɴꜱᴜꜰꜰɪᴄɪᴇɴᴛ ᴄᴏɪɴꜱ!\n\nʏᴏᴜ ɴᴇᴇᴅ 100 🪙 ᴄᴏɪɴꜱ ᴛᴏ ᴄᴏɴᴠᴇʀᴛ ᴛᴏ 1 💎 ɢᴇᴍ."
        )
    ok, result = await convert_coins_to_gems(message.from_user.id, amount)
    if not ok:
        if result == "insufficient":
            return await message.reply(
                "❌ ɪɴꜱᴜꜰꜰɪᴄɪᴇɴᴛ ᴄᴏɪɴꜱ!\n\nʏᴏᴜ ɴᴇᴇᴅ 100 🪙 ᴄᴏɪɴꜱ ᴛᴏ ᴄᴏɴᴠᴇʀᴛ ᴛᴏ 1 💎 ɢᴇᴍ."
            )
        return await message.reply("❌ ᴄᴏɴᴠᴇʀꜱɪᴏɴ ꜰᴀɪʟᴇᴅ.")

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT coins, gems FROM users WHERE user_id=?", (message.from_user.id,)) as cur:
            row = await cur.fetchone()
    coins, gems = row if row else (0, 0)

    await message.reply(
        f"✅ <b>ᴄᴏɴᴠᴇʀꜱɪᴏɴ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ!</b>\n\n"
        f"🪙 -{result * 100} ᴄᴏɪɴꜱ\n"
        f"💎 +{result} ɢᴇᴍ\n\n"
        f"ʏᴏᴜʀ ʙᴀʟᴀɴᴄᴇ:\n"
        f"🪙 ᴄᴏɪɴꜱ: <b>{coins:,}</b>\n"
        f"💎 ɢᴇᴍꜱ:  <b>{gems:,}</b>"
    )
