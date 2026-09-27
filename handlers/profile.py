from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from keyboards.main_menu import back_main_kb
from utils.database import (
    get_or_create_user, get_user_by_astral_id, get_user_by_username,
    convert_coins_to_gems,
)
from utils.ui import smart_edit
from utils.styler import fancy

router = Router()


def format_profile(u) -> str:
    # u = (user_id, username, first_name, astral_id, coins, gems, xp, ...)
    name = u[2] or "ᴜηᴋησωη"
    uname = f"@{u[1]}" if u[1] else "ησηє"
    astral_id = u[3] or "—"
    coins = u[4]
    gems = u[5]
    xp = u[6]
    quiz_solved = u[8]
    word_score = u[10]
    return (
        f"👤 <b>ᴩʀσғiʟє</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"✨ ηᴧϻє      — <b>{name}</b>\n"
        f"😄 ᴜsєʀηᴧϻє — {uname}\n"
        f"🚀 ᴧsтʀᴧʟ iᴅ  — <code>{astral_id}</code>\n\n"
        f"🪙 ᴄσiηs        — <b>{coins:,}</b>\n"
        f"📈 xᴩ           — <b>{xp:,}</b>\n"
        f"🧠 ǫᴜiᴢ sσʟᴠєᴅ  — <b>{quiz_solved}</b>\n"
        f"🏆 ᴡσʀᴅ sᴄσʀє  — <b>{word_score:,}</b>\n"
        f"💎 ɢєϻs         — <b>{gems:,}</b>"
    )


@router.message(F.text.regexp(r"^/profile(\s|$)"))
async def cmd_profile(message: Message):
    # Reply to a user
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
        await get_or_create_user(target.id, target.username, target.first_name)
        # fetch
        from utils.database import get_user_by_astral_id  # noqa
        async with __import__("aiosqlite").connect(__import__("config").DB_PATH) as db:
            async with db.execute("SELECT * FROM users WHERE user_id=?", (target.id,)) as cur:
                u = await cur.fetchone()
        if not u:
            return await message.reply("❌ ᴜsєʀ ησт ғσᴜηᴅ.")
        return await message.reply(format_profile(u))

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        u = await get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
        if not u:
            return await message.reply("❌ ᴜsєʀ ησт ғσᴜηᴅ.")
        return await message.reply(format_profile(u))

    arg = parts[1].strip()

    if arg.startswith("@"):
        u = await get_user_by_username(arg)
    elif arg.isdigit() and len(arg) == 6:
        u = await get_user_by_astral_id(arg)
    elif arg.isdigit():
        # treat as user_id
        import aiosqlite
        from config import DB_PATH
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT * FROM users WHERE user_id=?", (int(arg),)) as cur:
                u = await cur.fetchone()
    else:
        return await message.reply("❌ ɪηᴠᴧʟiᴅ. ᴜsє @username ᴏʀ ᴧsтʀᴧʟ iᴅ.")

    if not u:
        return await message.reply("❌ ᴜsєʀ ησт ғσᴜηᴅ.")
    await message.reply(format_profile(u))


@router.message(F.text.regexp(r"^/convert(\s|$)"))
async def cmd_convert(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return await message.reply(
            "ᴜsᴧɢє: <code>/convert 100ᴄ</code>\n"
            "100 ᴄσiηs = 1 ɢєϻ"
        )
    arg = parts[1].strip().lower().replace("c", "").replace(" ", "")
    if not arg.isdigit():
        return await message.reply("❌ ɪηᴠᴧʟiᴅ ᴧϻσᴜηт.")
    amount = int(arg)
    if amount < 100:
        return await message.reply(
            "❌ iηsᴜғғiᴄiєηт ᴄσiηs!\n\n"
            "ʏσᴜ ηєєᴅ 100 🪙 ᴄσiηs тσ ᴄσηᴠєʀт iηтσ 1 💎 ɢєϻ."
        )
    ok, result = await convert_coins_to_gems(message.from_user.id, amount)
    if not ok:
        if result == "insufficient":
            return await message.reply(
                "❌ iηsᴜғғiᴄiєηт ᴄσiηs!\n\n"
                "ʏσᴜ ηєєᴅ 100 🪙 ᴄσiηs тσ ᴄσηᴠєʀт iηтσ 1 💎 ɢєϻ."
            )
        return await message.reply("❌ ᴄσηᴠєʀsiση ғᴧiʟєᴅ.")

    # Fetch new balance
    import aiosqlite
    from config import DB_PATH
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT coins, gems FROM users WHERE user_id=?", (message.from_user.id,)) as cur:
            row = await cur.fetchone()
    coins, gems = row if row else (0, 0)

    await message.reply(
        f"✅ <b>ᴄσηᴠєʀsiση sᴜᴄᴄєssғᴜʟ!</b>\n\n"
        f"🪙 -{result * 100} ᴄσiηs\n"
        f"💎 +{result} ɢєϻ\n\n"
        f"ʏσᴜʀ ʙᴧʟᴧηᴄє:\n"
        f"🪙 ᴄσiηs: <b>{coins:,}</b>\n"
        f"💎 ɢєϻs:  <b>{gems:,}</b>"
    )
