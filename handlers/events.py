import asyncio
import logging
import random
from datetime import datetime, timedelta

from aiogram import Bot, Router, F
from aiogram.dispatcher.event.bases import SkipHandler
from aiogram.types import Message

from config import (
    EVENT_INTERVAL_SECONDS, EVENT_TIME_LIMIT_MINUTES,
    EVENT_PRIZE_MIN, EVENT_PRIZE_MAX,
    EVENT_NUMBER_MIN, EVENT_NUMBER_MAX,
    EVENT_MAX_GUESSES, EVENT_MAX_WINS_PER_DAY, BOT_ADMIN_IDS,
)
from utils.database import (
    get_all_active_groups, add_coins, add_xp, get_user_coins,
    get_or_create_user, record_event_win,
    count_event_wins_total, count_event_wins_today,
)

router = Router()
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════
# IN-MEMORY EVENT STATE
# chat_id -> {
#     "secret": int, "prize": int,
#     "expires_at": datetime,
#     "user_guesses": {user_id: {"count": int, "low": int, "high": int}}
# }
# ═══════════════════════════════════════════════
ACTIVE_EVENTS = {}


def _event_post_text(prize: int) -> str:
    return (
        f"📦 <b>ɴᴇᴡ ᴇᴠᴇɴᴛ ᴅʀᴏᴘᴘᴇᴅ:</b> ɢᴜᴇꜱꜱ ᴛʜᴇ ꜱᴇᴄʀᴇᴛ 3-ᴅɪɢɪᴛ "
        f"ɴᴜᴍʙᴇʀ ᴛᴏ ᴡɪɴ ᴛʜᴇ ᴄᴏɪɴꜱ.\n\n"
        f"💰 ᴘʀɪᴢᴇ: <b>{prize:,} ᴄᴏɪɴꜱ</b>\n"
        f"🎯 ʀᴀɴɢᴇ: [ <b>{EVENT_NUMBER_MIN} ──── {EVENT_NUMBER_MAX}</b> ]\n"
        f"🕹️ ɢᴜᴇꜱꜱ ᴜꜱɪɴɢ: <code>/h &lt;number&gt;</code>\n"
        f"⏳ ᴛɪᴍᴇ ʟɪᴍɪᴛ: <b>{EVENT_TIME_LIMIT_MINUTES} ᴍɪɴᴜᴛᴇꜱ</b>\n\n"
        f"ꜰɪʀꜱᴛ ᴘᴇʀꜱᴏɴ ᴛᴏ ɢᴜᴇꜱꜱ ᴛʜᴇ ʀɪɢʜᴛ ɴᴜᴍʙᴇʀ ᴡɪɴꜱ!"
    )


async def _post_event(bot: Bot, chat_id: int):
    secret = random.randint(EVENT_NUMBER_MIN, EVENT_NUMBER_MAX)
    prize = random.randint(EVENT_PRIZE_MIN, EVENT_PRIZE_MAX)
    expires = datetime.utcnow() + timedelta(minutes=EVENT_TIME_LIMIT_MINUTES)

    ACTIVE_EVENTS[chat_id] = {
        "secret": secret,
        "prize": prize,
        "expires_at": expires,
        "user_guesses": {},
    }

    try:
        await bot.send_message(chat_id, _event_post_text(prize))
        logger.info(f"Event in {chat_id}: secret={secret}, prize={prize}")
    except Exception as e:
        logger.warning(f"Event post failed in {chat_id}: {e}")


async def event_poster_loop(bot: Bot):
    """Every EVENT_INTERVAL_SECONDS, post a unique event per GC."""
    await asyncio.sleep(20)
    while True:
        try:
            groups = await get_all_active_groups()
            now = datetime.utcnow()
            for gid in groups:
                ev = ACTIVE_EVENTS.get(gid)
                if ev and ev["expires_at"] > now:
                    continue
                if ev:
                    ACTIVE_EVENTS.pop(gid, None)
                await _post_event(bot, gid)
                await asyncio.sleep(2)
        except Exception as e:
            logger.error(f"event_poster_loop: {e}")
        await asyncio.sleep(EVENT_INTERVAL_SECONDS)


# ═══════════════════════════════════════════════
# /h — EVENT GUESS HANDLER (higher priority)
# ═══════════════════════════════════════════════
@router.message(F.text.regexp(r"^/h(\s|$)"))
async def event_guess_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Check if there's an active event in this chat
    ev = ACTIVE_EVENTS.get(chat_id)
    if not ev:
        # No event → pass to personal game in tgames.py
        raise SkipHandler()

    # Check expiry
    if ev["expires_at"] <= datetime.utcnow():
        ACTIVE_EVENTS.pop(chat_id, None)
        return await message.reply("⏳ ᴛʜᴇ ᴇᴠᴇɴᴛ ʜᴀꜱ ᴇxᴘɪʀᴇᴅ. ᴡᴀɪᴛ ꜰᴏʀ ᴛʜᴇ ɴᴇxᴛ ᴅʀᴏᴘ.")

    # Parse guess
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip().isdigit():
        return await message.reply("ᴜꜱᴀɢᴇ: <code>/h 250</code>")

    guess = int(parts[1].strip())
    if not (EVENT_NUMBER_MIN <= guess <= EVENT_NUMBER_MAX):
        return await message.reply(
            f"❌ ɢᴜᴇꜱꜱ ʙᴇᴛᴡᴇᴇɴ {EVENT_NUMBER_MIN} ᴀɴᴅ {EVENT_NUMBER_MAX}."
        )

    # Check per-user daily limit
    wins_today = await count_event_wins_today(user_id, chat_id)
    if wins_today >= EVENT_MAX_WINS_PER_DAY:
        return await message.reply(
            f"⏳ ʏᴏᴜ'ᴠᴇ ʀᴇᴀᴄʜᴇᴅ ᴛʜᴇ ᴅᴀɪʟʏ ʟɪᴍɪᴛ ({EVENT_MAX_WINS_PER_DAY} ᴡɪɴꜱ).\n"
            f"ᴄᴏᴍᴇ ʙᴀᴄᴋ ᴛᴏᴍᴏʀʀᴏᴡ."
        )

    # Initialize user's guess state
    ug = ev["user_guesses"].setdefault(user_id, {
        "count": 0,
        "low": EVENT_NUMBER_MIN,
        "high": EVENT_NUMBER_MAX,
    })

    if ug["count"] >= EVENT_MAX_GUESSES:
        return await message.reply(
            f"❌ ʏᴏᴜ'ᴠᴇ ᴜꜱᴇᴅ ᴀʟʟ {EVENT_MAX_GUESSES} ɢᴜᴇꜱꜱᴇꜱ ꜰᴏʀ ᴛʜɪꜱ ᴇᴠᴇɴᴛ."
        )

    ug["count"] += 1
    remaining = EVENT_MAX_GUESSES - ug["count"]
    secret = ev["secret"]

    # ═══ CORRECT GUESS ═══
    if guess == secret:
        prize = ev["prize"]
        await get_or_create_user(user_id, message.from_user.username, message.from_user.first_name)
        await add_coins(user_id, prize)
        await add_xp(user_id, 20)
        await record_event_win(user_id, chat_id, prize)

        new_balance = await get_user_coins(user_id)
        total_wins = await count_event_wins_total(user_id, chat_id)
        today_wins = await count_event_wins_today(user_id, chat_id)

        ACTIVE_EVENTS.pop(chat_id, None)

        return await message.reply(
            f"🎉 ᴄᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴꜱ {message.from_user.mention_html()}! "
            f"ʏᴏᴜ ɢᴜᴇꜱꜱᴇᴅ ᴛʜᴇ ʀɪɢʜᴛ ɴᴜᴍʙᴇʀ.\n\n"
            f"🔑 ꜱᴇᴄʀᴇᴛ ɴᴜᴍʙᴇʀ: <b>{secret}</b>\n"
            f"💰 ᴘʀɪᴢᴇ ᴡᴏɴ: <b>+{prize:,}</b>\n"
            f"💼 ɴᴇᴡ ʙᴀʟᴀɴᴄᴇ: <b>{new_balance:,}</b>\n"
            f"🏆 ᴛᴏᴛᴀʟ ᴅʀᴏᴘꜱ ᴡᴏɴ ʜᴇʀᴇ: <b>{total_wins}</b>\n"
            f"📅 ᴡɪɴꜱ ᴛᴏᴅᴀʏ: <b>{today_wins}/{EVENT_MAX_WINS_PER_DAY}</b>"
        )

    # ═══ HIGH / LOW FEEDBACK ═══
    if guess > secret:
        # HIGH guess → 📈 UP arrow (matches Baka style)
        ug["high"] = min(ug["high"], guess - 1)
        arrow = "📈"
        label = "ᴛᴏᴏ ʜɪɢʜ"
    else:
        # LOW guess → 📉 DOWN arrow
        ug["low"] = max(ug["low"], guess + 1)
        arrow = "📉"
        label = "ᴛᴏᴏ ʟᴏᴡ"

    # If bounds collapse (bad luck with limit)
    if ug["low"] >= ug["high"]:
        ug["low"] = EVENT_NUMBER_MIN
        ug["high"] = EVENT_NUMBER_MAX

    await message.reply(
        f"{arrow} [ <b>{guess}</b> ] ɪꜱ {label}!\n"
        f"🎯 ʀᴀɴɢᴇ: [ <b>{ug['low']} ──── {ug['high']}</b> ]\n"
        f"⚠️ ɢᴜᴇꜱꜱᴇꜱ ʟᴇꜰᴛ: <b>{remaining}</b>"
    )


# ═══════════════════════════════════════════════
# /event — admin manual trigger
# ═══════════════════════════════════════════════
@router.message(F.text.regexp(r"^/event(\s|$)"))
async def cmd_event(message: Message, bot: Bot):
    if message.from_user.id not in BOT_ADMIN_IDS:
        return
    if message.chat.type == "private":
        return await message.reply("📩 ᴜꜱᴇ ɪɴ ɢʀᴏᴜᴘꜱ ᴏɴʟʏ.")
    await _post_event(bot, message.chat.id)
