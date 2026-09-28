import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import ErrorEvent

from config import BOT_TOKEN, BOT_NAME
from handlers import (
    start, menu, profile, robs, leaderboard, daily, study, mission,
    shop, powers, admin, quiz, events, tgames,
)
from utils.logger import setup_logger
from utils.database import init_db, get_all_active_groups
from utils.quiz_loader import background_load


async def main():
    setup_logger()
    logging.info(f"🚀 Starting {BOT_NAME} ...")

    if not BOT_TOKEN:
        raise RuntimeError("❌ BOT_TOKEN missing!")

    await init_db()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    @dp.errors()
    async def on_error(event: ErrorEvent):
        logging.error(f"⚠️ Error: {event.exception}")
        return True

    # ═══ ROUTER ORDER ═══
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
    dp.include_router(admin.router)
    dp.include_router(quiz.router)
    dp.include_router(events.router)    # 👈 BEFORE tgames
    dp.include_router(tgames.router)    # 👈 LAST

    # ═══ BACKGROUND TASKS ═══
    asyncio.create_task(events.event_poster_loop(bot))
    asyncio.create_task(background_load())

    # Log registered groups on startup
    try:
        groups = await get_all_active_groups()
        logging.info(f"📋 Registered groups for events: {len(groups)}")
        for g in groups[:5]:
            logging.info(f"  • {g}")
    except Exception as e:
        logging.warning(f"Group count check: {e}")

    logging.info("✅ Bot is running.")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("🛑 Bot stopped.")
