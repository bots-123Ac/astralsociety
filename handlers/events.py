import asyncio
import logging
import random
from datetime import datetime, timedelta

from aiogram import Bot, Router, F
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

# ═══ IN-MEMORY EVENT STATE ═══
# chat_id -> {"secret": int, "prize": int, "expires_at": datetime,
#             "user_guesses": {user_id: {"count": int, "low": int, "high": int}}}
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
        logger.info(f"✅ Event posted in {chat_id}: secret={secret}, prize={prize}")
        return True
    except Exception as e:
        logger.warning(f"❌ Event post failed in {chat_id}: {e}")
        return False


async def event_poster_loop(bot: Bot):
    """Fully automatic — posts events every EVENT_INTERVAL_SECONDS in all GCs."""
    await asyncio.sleep(20)  # wait for bot startup
    logger.info("🎯 Event poster loop STARTED")

    while True:
        try:
            groups = await get_all_active_groups()
            now = datetime.utcnow()
            logger.info(f"🔍 Event cycle: {len(groups)} registered groups")

            posted = 0
            for gid in groups:
                ev = ACTIVE_EVENTS.get(gid)
                if ev and ev["expires_at"] > now:
                    continue  # still active
                if ev:
                    ACTIVE_EVENTS.pop(gid, None)
                if await _post_event(bot, gid):
                    posted += 1
                await asyncio.sleep(2)

            if posted:
                logger.info(f"✅ Posted {posted} event(s) this cycle")

        except Exception as e:
            logger.error(f"event_poster_loop: {e}")

        await asyncio.sleep(EVENT_INTERVAL_SECONDS)


# ═══════════════════════════════════════════════
# PUBLIC: Try to handle /h as event guess
# Returns True if handled by event, False otherwise
# ═══════════════════════════════════════════════
async def try_handle_event_guess(message: Message) -> bool:
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Only in groups
    if message.chat.type not in ("group", "supergroup"):
        return False

    ev = ACTIVE_EVENTS.get(chat_id)
    if not ev:
        return False

    if ev["expires_at"] <= datetime.utcnow():
        ACTIVE_EVENTS.pop(chat_id, None)
        await message.reply("⏳ ᴛʜᴇ ᴇᴠᴇɴᴛ ʜᴀꜱ ᴇxᴘɪʀᴇᴅ.")
        return True

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip().isdigit():
        await message.reply("ᴜꜱᴀɢᴇ: <code>/h 250</code>")
        return True

    guess = int(parts[1].strip())
    if not (EVENT_NUMBER_MIN <= guess <= EVENT_NUMBER_MAX):
        await message.reply(
            f"❌ ɢᴜᴇꜱꜱ ʙᴇᴛᴡᴇᴇɴ {EVENT_NUMBER_MIN} ᴀɴᴅ {EVENT_NUMBER_MAX}."
        )
        return True

    wins_today = await count_event_wins_today(user_id, chat_id)
    if wins_today >= EVENT_MAX_WINS_PER_DAY:
        await message.reply(
            f"⏳ ʏᴏᴜ'ᴠᴇ ʀᴇᴀᴄʜᴇᴅ ᴛʜᴇ ᴅᴀɪʟʏ ʟɪᴍɪᴛ ({EVENT_MAX_WINS_PER_DAY} ᴡɪɴꜱ).\n"
            f"ᴄᴏᴍᴇ ʙᴀᴄᴋ ᴛᴏᴍᴏʀʀᴏᴡ."
        )
        return True

    ug = ev["user_guesses"].setdefault(user_id, {
        "count": 0,
        "low": EVENT_NUMBER_MIN,
        "high": EVENT_NUMBER_MAX,
    })

    if ug["count"] >= EVENT_MAX_GUESSES:
        await message.reply(
            f"❌ ʏᴏᴜ'ᴠᴇ ᴜꜱᴇᴅ ᴀʟʟ {EVENT_MAX_GUESSES} ɢᴜᴇꜱꜱᴇꜱ ꜰᴏʀ ᴛʜɪꜱ ᴇᴠᴇɴᴛ."
        )
        return True

    ug["count"] += 1
    remaining = EVENT_MAX_GUESSES - ug["count"]
    secret = ev["secret"]

    # ═══ CORRECT ═══
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

        await message.reply(
            f"🎉 ᴄᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴꜱ {message.from_user.mention_html()}! "
            f"ʏᴏᴜ ɢᴜᴇꜱꜱᴇᴅ ᴛʜᴇ ʀɪɢʜᴛ ɴᴜᴍʙᴇʀ.\n\n"
            f"🔑 ꜱᴇᴄʀᴇᴛ ɴᴜᴍʙᴇʀ: <b>{secret}</b>\n"
            f"💰 ᴘʀɪᴢᴇ ᴡᴏɴ: <b>+{prize:,}</b>\n"
            f"💼 ɴᴇᴡ ʙᴀʟᴀɴᴄᴇ: <b>{new_balance:,}</b>\n"
            f"🏆 ᴛᴏᴛᴀʟ ᴅʀᴏᴘꜱ ᴡᴏɴ ʜᴇʀᴇ: <b>{total_wins}</b>\n"
            f"📅 ᴡɪɴꜱ ᴛᴏᴅᴀʏ: <b>{today_wins}/{EVENT_MAX_WINS_PER_DAY}</b>"
        )
        return True

    # ═══ FEEDBACK ═══
    if guess > secret:
        ug["high"] = min(ug["high"], guess - 1)
        arrow, label = "📈", "ᴛᴏᴏ ʜɪɢʜ"
    else:
        ug["low"] = max(ug["low"], guess + 1)
        arrow, label = "📉", "ᴛᴏᴏ ʟᴏᴡ"

    if ug["low"] >= ug["high"]:
        ug["low"] = EVENT_NUMBER_MIN
        ug["high"] = EVENT_NUMBER_MAX

    await message.reply(
        f"{arrow} [ <b>{guess}</b> ] ɪꜱ {label}!\n"
        f"🎯 ʀᴀɴɢᴇ: [ <b>{ug['low']} ──── {ug['high']}</b> ]\n"
        f"⚠️ ɢᴜᴇꜱꜱᴇꜱ ʟᴇꜰᴛ: <b>{remaining}</b>"
    )
    return True


# ═══════════════════════════════════════════════
# /event — admin manual trigger (optional)
# ═══════════════════════════════════════════════
@router.message(F.text.regexp(r"^/event(\s|$)"))
async def cmd_event(message: Message, bot: Bot):
    if message.from_user.id not in BOT_ADMIN_IDS:
        return
    if message.chat.type == "private":
        return await message.reply("📩 ᴜꜱᴇ ɪɴ ɢʀᴏᴜᴘꜱ ᴏɴʟʏ.")
    await _post_event(bot, message.chat.id)
