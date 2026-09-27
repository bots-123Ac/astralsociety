import asyncio
import logging
import random
from datetime import datetime, timedelta

from aiogram import Bot
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Router

from config import (
    EVENT_INTERVAL_SECONDS, EVENT_TIME_LIMIT_MINUTES,
    EVENT_PRIZE_MIN, EVENT_PRIZE_MAX,
    EVENT_NUMBER_MIN, EVENT_NUMBER_MAX,
)
from utils.database import get_all_active_groups, add_coins, add_xp

router = Router()
logger = logging.getLogger(__name__)

# Per-group active events: chat_id -> {secret, prize, expires_at, started_at}
ACTIVE_EVENTS = {}


def _event_text(prize: int) -> str:
    return (
        f"📦 <b>ɴᴇᴡ ᴇᴠᴇɴᴛ ᴅʀᴏᴘᴘᴇᴅ!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎯 ɢᴜᴇꜱꜱ ᴛʜᴇ ꜱᴇᴄʀᴇᴛ 3-ᴅɪɢɪᴛ ɴᴜᴍʙᴇʀ\n\n"
        f"💰 ᴘʀɪᴢᴇ: <b>{prize:,}</b> ᴄᴏɪɴꜱ\n"
        f"🎯 ʀᴀɴɢᴇ: <b>100 — 500</b>\n"
        f"🎮 ɢᴜᴇꜱꜱ ᴜꜱɪɴɢ: <code>/h &lt;number&gt;</code>\n"
        f"⏳ ᴛɪᴍᴇ ʟɪᴍɪᴛ: <b>{EVENT_TIME_LIMIT_MINUTES} ᴍɪɴᴜᴛᴇꜱ</b>\n\n"
        f"🏁 <i>First person to guess wins!</i>"
    )


async def _post_event(bot: Bot, chat_id: int):
    secret = random.randint(EVENT_NUMBER_MIN, EVENT_NUMBER_MAX)
    prize = random.randint(EVENT_PRIZE_MIN, EVENT_PRIZE_MAX)
    expires = datetime.utcnow() + timedelta(minutes=EVENT_TIME_LIMIT_MINUTES)
    ACTIVE_EVENTS[chat_id] = {
        "secret": secret,
        "prize": prize,
        "expires_at": expires,
    }
    try:
        await bot.send_message(chat_id, _event_text(prize))
        logger.info(f"Event posted in {chat_id}: secret={secret}, prize={prize}")
    except Exception as e:
        logger.warning(f"Failed to post event in {chat_id}: {e}")


async def event_poster_loop(bot: Bot):
    """Every EVENT_INTERVAL_SECONDS, post a unique event in every active group."""
    # Initial delay so bot finishes startup
    await asyncio.sleep(30)
    while True:
        try:
            groups = await get_all_active_groups()
            now = datetime.utcnow()
            for gid in groups:
                # Skip if an unexpired event exists
                ev = ACTIVE_EVENTS.get(gid)
                if ev and ev["expires_at"] > now:
                    continue
                # Expire old event if any
                if ev:
                    ACTIVE_EVENTS.pop(gid, None)
                await _post_event(bot, gid)
                await asyncio.sleep(2)  # avoid flood
        except Exception as e:
            logger.error(f"event_poster_loop error: {e}")
        await asyncio.sleep(EVENT_INTERVAL_SECONDS)


async def check_event_guess(message: Message) -> bool:
    """Return True if this message was a valid event guess."""
    chat_id = message.chat.id
    if chat_id not in ACTIVE_EVENTS:
        return False
    ev = ACTIVE_EVENTS[chat_id]
    if ev["expires_at"] <= datetime.utcnow():
        ACTIVE_EVENTS.pop(chat_id, None)
        return False
    return True


async def handle_event_guess(message: Message, guess: int) -> bool:
    chat_id = message.chat.id
    ev = ACTIVE_EVENTS.get(chat_id)
    if not ev:
        return False
    if ev["expires_at"] <= datetime.utcnow():
        ACTIVE_EVENTS.pop(chat_id, None)
        return False

    if guess == ev["secret"]:
        prize = ev["prize"]
        await add_coins(message.from_user.id, prize)
        await add_xp(message.from_user.id, 10)
        ACTIVE_EVENTS.pop(chat_id, None)
        await message.reply(
            f"🎉 <b>{message.from_user.mention_html()} ᴡᴏɴ ᴛʜᴇ ᴇᴠᴇɴᴛ!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🎯 ꜱᴇᴄʀᴇᴛ ɴᴜᴍʙᴇʀ: <b>{ev['secret']}</b>\n"
            f"🪙 ᴘʀɪᴢᴇ: <b>+{prize:,} ᴄᴏɪɴꜱ</b>\n"
            f"📈 xᴘ: <b>+10</b>"
        )
        return True

    # Wrong — send hint
    if guess < ev["secret"]:
        await message.reply(f"⬆️ <b>{guess} ɪꜱ ᴠᴇʀʏ ʟᴏᴡ</b>\nʀᴀɴɢᴇ: {guess}–500")
    else:
        await message.reply(f"⬇️ <b>{guess} ɪꜱ ᴠᴇʀʏ ʜɪɢʜ</b>\nʀᴀɴɢᴇ: 100–{guess}")
    return True


@router.message(Command("event"))
async def cmd_event(message: Message, bot: Bot):
    """Admin can manually trigger event."""
    from config import BOT_ADMIN_IDS
    if message.from_user.id not in BOT_ADMIN_IDS:
        return
    if message.chat.type == "private":
        return await message.reply("📩 ᴜꜱᴇ ɪɴ ɢʀᴏᴜᴘꜱ ᴏɴʟʏ.")
    await _post_event(bot, message.chat.id)
