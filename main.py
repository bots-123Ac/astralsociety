import asyncio
import logging

from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import ErrorEvent

from config import BOT_TOKEN, BOT_NAME
from handlers import (
    start, menu, profile, robs, leaderboard, daily, study, mission,
    shop, powers, quiz, premium, tgames, treasure, luckydoor,
    botstats, admin,
)
from utils.logger import setup_logger
from utils.database import (
    init_db, close_pool, get_pool, log_user_activity,
    get_active_shields, parse_dt, now_utc,
)
from utils.quiz_loader import background_load


# ═══════════════════════════════════════════════
# ACTIVITY MIDDLEWARE
# ═══════════════════════════════════════════════
_activity_cache = set()


class ActivityMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        try:
            user = getattr(event, "from_user", None)
            if user and not user.is_bot:
                if user.id not in _activity_cache:
                    _activity_cache.add(user.id)
                    asyncio.create_task(log_user_activity(user.id))
        except Exception:
            pass
        return await handler(event, data)


# ═══════════════════════════════════════════════
# SHIELD EXPIRY ALERT LOOP
# Sends DM at 6h, 2h, 30m remaining
# ═══════════════════════════════════════════════
async def shield_alert_loop(bot: Bot):
    await asyncio.sleep(45)  # startup delay
    print("⏰ Shield alert loop STARTED")

    # user_id -> {"until": str, "sent": set}
    _alerts: dict = {}

    while True:
        try:
            rows = await get_active_shields()
            now = now_utc()

            for user_id, until_str in rows:
                until = parse_dt(until_str)
                if not until:
                    continue

                remaining = (until - now).total_seconds()

                # Reset alert tracking for new shield period
                entry = _alerts.get(user_id)
                if not entry or entry["until"] != until_str:
                    _alerts[user_id] = {"until": until_str, "sent": set()}
                    entry = _alerts[user_id]

                alert_key = None
                alert_text = None

                # Priority: smallest remaining first (avoids spam if multiple missed)
                if remaining <= 30 * 60 and "30m" not in entry["sent"]:
                    alert_key = "30m"
                    alert_text = "30 ᴍɪɴᴜᴛᴇꜱ"
                elif remaining <= 2 * 3600 and "2h" not in entry["sent"]:
                    alert_key = "2h"
                    alert_text = "2 ʜᴏᴜʀꜱ"
                elif remaining <= 6 * 3600 and "6h" not in entry["sent"]:
                    alert_key = "6h"
                    alert_text = "6 ʜᴏᴜʀꜱ"

                if alert_key:
                    entry["sent"].add(alert_key)

                    # Mark any lower-priority (higher time) alerts as sent too
                    if alert_key == "30m":
                        entry["sent"].update(["6h", "2h"])
                    elif alert_key == "2h":
                        entry["sent"].add("6h")

                    try:
                        await bot.send_message(
                            user_id,
                            f"⚠️ <b>ᴀʟᴇʀᴛ!</b>\n\n"
                            f"ʏᴏᴜʀ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ᴡɪʟʟ ᴇɴᴅ ɪɴ ᴇxᴀᴄᴛʟʏ "
                            f"<b>{alert_text}</b>.\n"
                            f"👉 ᴜꜱᴇ /shield 2 ᴛᴏ ꜱᴛᴀʏ ꜱᴀꜰᴇ."
                        )
                        print(f"📩 Shield alert ({alert_key}) → {user_id}")
                    except Exception as e:
                        print(f"⚠️ Alert send failed for {user_id}: {e}")

            # Cleanup stale entries (user no longer has active shield)
            active_ids = {uid for uid, _ in rows}
            stale = [k for k in _alerts if k not in active_ids]
            for k in stale:
                _alerts.pop(k, None)

        except Exception as e:
            print(f"⚠️ Shield alert loop error: {e}")

        await asyncio.sleep(60)  # check every 1 minute


# ═══════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════
async def main():
    setup_logger()
    logging.info(f"🚀 Starting {BOT_NAME} ...")

    if not BOT_TOKEN:
        raise RuntimeError("❌ BOT_TOKEN missing!")

    await init_db()
    await get_pool()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Middleware
    dp.message.middleware(ActivityMiddleware())
    dp.callback_query.middleware(ActivityMiddleware())

    # Global error handler
    @dp.errors()
    async def on_error(event: ErrorEvent):
        logging.error(f"⚠️ Error: {event.exception}")
        return True

    # ═══ ROUTERS (admin LAST) ═══
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(profile.router)
    dp.include_router(robs.router)
    dp.include_router(leaderboard.router)
    dp.include_router(daily.router)
    dp.include_router(study.router)
    dp.include_router(mission.router)
    dp.include_router(shop.router)
    dp.include_router(powers.router)
    dp.include_router(quiz.router)
    dp.include_router(premium.router)
    dp.include_router(botstats.router)
    dp.include_router(treasure.router)
    dp.include_router(luckydoor.router)
    dp.include_router(tgames.router)
    dp.include_router(admin.router)

    # ═══ BACKGROUND TASKS ═══
    asyncio.create_task(background_load())
    asyncio.create_task(shield_alert_loop(bot))   # 👈 NEW

    logging.info("✅ Bot is running.")
    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await dp.start_polling(bot)
    finally:
        await close_pool()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("🛑 Bot stopped.")
