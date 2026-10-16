import asyncio
import logging

from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import ErrorEvent

from config import BOT_TOKEN, BOT_NAME, OWNER_ID
from handlers import (
    start, menu, profile, robs, leaderboard, daily, study, mission,
    shop, powers, quiz, premium, tgames, treasure, luckydoor,
    bombdefuse, botstats, admin, clone, required_chat, broadcast,
)
from utils.logger import setup_logger
from utils.database import init_db, close_pool, get_pool, log_user_activity
from utils.quiz_loader import background_load
from utils import clone_db
from utils import clone_manager
from utils.clone_middleware import CloneAccessMiddleware
from utils.permissions import set_current_bot_context


# ═══════════════════════════════════════════════
# ACTIVITY MIDDLEWARE
# ═══════════════════════════════════════════════
_activity_cache: set = set()


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
# BOT-CONTEXT MIDDLEWARE
# ═══════════════════════════════════════════════
class BotContextMiddleware(BaseMiddleware):
    """
    Sets the current bot's owner id in a contextvar so that
    utils.permissions.is_owner / is_bot_admin return the correct
    value for the bot that is currently handling the update.
    """
    def __init__(self, bot_owner_id: int, is_clone: bool = False):
        self.bot_owner_id = bot_owner_id
        self.is_clone = is_clone

    async def __call__(self, handler, event, data):
        set_current_bot_context(self.bot_owner_id, self.is_clone)
        return await handler(event, data)


# ═══════════════════════════════════════════════
# DISPATCHER FACTORY
# ═══════════════════════════════════════════════
def build_dispatcher(bot_owner_id: int, is_clone: bool = False,
                     clone_id: int | None = None) -> Dispatcher:
    """
    Build a fully configured Dispatcher.
    Used for BOTH main bot and every clone bot.
    """
    dp = Dispatcher()

    # ── Middlewares (order matters) ──
    dp.message.middleware(ActivityMiddleware())
    dp.callback_query.middleware(ActivityMiddleware())

    dp.message.middleware(BotContextMiddleware(bot_owner_id, is_clone))
    dp.callback_query.middleware(BotContextMiddleware(bot_owner_id, is_clone))

    if is_clone and clone_id is not None:
        cam = CloneAccessMiddleware(clone_id)
        dp.message.middleware(cam)
        dp.callback_query.middleware(cam)

    # ── Global error handler ──
    @dp.errors()
    async def on_error(event: ErrorEvent):
        logging.error(f"⚠️ Error: {event.exception}")
        return True

    # ═══════════════════════════════════════════════
    # ROUTER ORDER — VERY IMPORTANT
    # admin.router MUST be LAST (has wildcard handler)
    # ═══════════════════════════════════════════════
    dp.include_router(start.router)          # 1.  /start + my_chat_member
    dp.include_router(menu.router)           # 2.  /help, /about
    dp.include_router(profile.router)        # 3.  /balance, /profile, /convert
    dp.include_router(robs.router)           # 4.  /gives, /robs, /shield, /shieldcheck
    dp.include_router(leaderboard.router)    # 5.  /aleaderboard
    dp.include_router(daily.router)          # 6.  /daily, /performance
    dp.include_router(study.router)          # 7.  /study
    dp.include_router(mission.router)        # 8.  /mission
    dp.include_router(shop.router)           # 9.  /shop
    dp.include_router(powers.router)         # 10. /powers
    dp.include_router(quiz.router)           # 11. /quiz
    dp.include_router(premium.router)        # 12. /premium, /premiumstatus, /setemoji
    dp.include_router(clone.router)          # 13. /clone, /myclone, /deleteclone + FSM
    dp.include_router(required_chat.router)  # 14. /addrequired, /removerequired, /listrequired
    dp.include_router(broadcast.router)      # 15. /broadcast, /broadcast_users, ...
    dp.include_router(botstats.router)       # 16. /botstatus, /users
    dp.include_router(treasure.router)       # 17. /treasure
    dp.include_router(luckydoor.router)      # 18. /luckydoor
    dp.include_router(bombdefuse.router)     # 19. /defuse
    dp.include_router(tgames.router)         # 20. /tgames, /h
    dp.include_router(admin.router)          # 21. LAST — /admin + wildcard

    return dp


# ═══════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════
async def main():
    setup_logger()
    logging.info(f"🚀 Starting {BOT_NAME} ...")

    if not BOT_TOKEN:
        raise RuntimeError("❌ BOT_TOKEN missing!")

    # ── DB init ──
    await init_db()
    await clone_db.init_clone_tables()
    await get_pool()

    # ── Main bot ──
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = build_dispatcher(bot_owner_id=OWNER_ID, is_clone=False)

    # ── Wire clone dispatcher factory ──
    def _factory(clone_record):
        return build_dispatcher(
            bot_owner_id=clone_record["owner_user_id"],
            is_clone=True,
            clone_id=clone_record["id"],
        )

    clone_manager.set_dispatcher_factory(_factory)

    # ── Background tasks ──
    asyncio.create_task(background_load())

    # ── Load all active clones ──
    await clone_manager.load_all_clones()

    # ── Start membership checker (uses MAIN bot to verify join status) ──
    clone_manager.start_membership_checker(bot)

    logging.info("✅ Bot is running.")
    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await dp.start_polling(bot)
    finally:
        logging.info("🛑 Shutting down...")
        try:
            await clone_manager.stop_membership_checker()
        except Exception:
            pass
        try:
            await clone_manager.stop_all_clones()
        except Exception:
            pass
        await close_pool()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("🛑 Bot stopped.")
