import asyncio
import logging

from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import ErrorEvent

from config import BOT_TOKEN, BOT_NAME
from handlers import (
    start, menu, profile, robs, leaderboard, daily, study, mission,
    shop, powers, quiz, premium, tgames, botstats, admin,
)
from utils.logger import setup_logger
from utils.database import init_db, close_pool, get_pool, log_user_activity
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

    dp.message.middleware(ActivityMiddleware())
    dp.callback_query.middleware(ActivityMiddleware())

    @dp.errors()
    async def on_error(event: ErrorEvent):
        logging.error(f"⚠️ Error: {event.exception}")
        return True

    # ═══════════════════════════════════════════════
    # ROUTER ORDER — VERY IMPORTANT
    # admin.router MUST be LAST (has wildcard handler)
    # ═══════════════════════════════════════════════
    dp.include_router(start.router)         # 1. /start
    dp.include_router(menu.router)          # 2. /help, /about
    dp.include_router(profile.router)       # 3. /profile, /convert
    dp.include_router(robs.router)          # 4. /gives, /robs, /shield
    dp.include_router(leaderboard.router)   # 5. /aleaderboard
    dp.include_router(daily.router)         # 6. /daily, /performance
    dp.include_router(study.router)         # 7. /study
    dp.include_router(mission.router)       # 8. /mission
    dp.include_router(shop.router)          # 9. /shop
    dp.include_router(powers.router)        # 10. /powers
    dp.include_router(quiz.router)          # 11. /quiz
    dp.include_router(premium.router)       # 12. /premium
    dp.include_router(botstats.router)      # 13. /botstatus, /users
    dp.include_router(tgames.router)        # 14. /tgames, /h
    dp.include_router(admin.router)         # 15. LAST — /admin + wildcard

    asyncio.create_task(background_load())

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
