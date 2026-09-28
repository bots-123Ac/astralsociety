import asyncio
import logging

from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import ErrorEvent

from config import BOT_TOKEN, BOT_NAME
from handlers import (
    start, menu, profile, robs, leaderboard, daily, study, mission,
    shop, powers, admin, quiz, events, tgames,
)
from utils.logger import setup_logger
from utils.database import init_db, get_all_active_groups, register_group
from utils.quiz_loader import background_load


# ═══════════════════════════════════════════════
# AUTO-REGISTER GROUPS ON EVERY MESSAGE
# ═══════════════════════════════════════════════
class GroupRegisterMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        try:
            chat = getattr(event, "chat", None)
            if chat and chat.type in ("group", "supergroup"):
                await register_group(chat.id, chat.title or "")
        except Exception:
            pass
        return await handler(event, data)


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

    # Auto-register groups
    dp.message.middleware(GroupRegisterMiddleware())

    @dp.errors()
    async def on_error(event: ErrorEvent):
        logging.error(f"⚠️ Error: {event.exception}")
        return True

    # ═══ ROUTER ORDER — events BEFORE tgames ═══
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
    dp.include_router(events.router)    # /event command
    dp.include_router(tgames.router)    # /h + /tgames

    # ═══ Background tasks ═══
    asyncio.create_task(events.event_poster_loop(bot))
    asyncio.create_task(background_load())

    # Startup log
    try:
        groups = await get_all_active_groups()
        logging.info(f"📋 Registered groups: {len(groups)}")
        for g in groups[:10]:
            logging.info(f"  • {g}")
    except Exception as e:
        logging.warning(f"Group check: {e}")

    logging.info("✅ Bot is running.")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("🛑 Bot stopped.")
