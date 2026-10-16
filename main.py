import asyncio
import importlib
import logging

from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import ErrorEvent

from config import BOT_TOKEN, BOT_NAME, OWNER_ID
from utils.logger import setup_logger
from utils.database import init_db, close_pool, get_pool, log_user_activity
from utils.quiz_loader import background_load
from utils import clone_db
from utils import clone_manager
from utils.clone_middleware import CloneAccessMiddleware
from utils.permissions import set_current_bot_context


# ═══════════════════════════════════════════════
# HANDLER MODULE LIST (order matters)
# admin MUST be last (has wildcard handler)
# ═══════════════════════════════════════════════
HANDLER_MODULE_NAMES = [
    "handlers.start",
    "handlers.menu",
    "handlers.profile",
    "handlers.robs",
    "handlers.leaderboard",
    "handlers.daily",
    "handlers.study",
    "handlers.mission",
    "handlers.shop",
    "handlers.powers",
    "handlers.quiz",
    "handlers.premium",
    "handlers.clone",
    "handlers.required_chat",
    "handlers.broadcast",
    "handlers.botstats",
    "handlers.treasure",
    "handlers.luckydoor",
    "handlers.bombdefuse",
    "handlers.tgames",
    "handlers.admin",       # MUST BE LAST
]


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
# FRESH ROUTER LOADER
# ═══════════════════════════════════════════════
def _load_fresh_routers():
    """
    Reload all handler modules and return fresh Router instances.

    aiogram v3 Router objects cannot be attached to multiple Dispatchers.
    To build a Dispatcher for a clone bot, we reload every handler module
    so each gets a brand-new Router instance.

    NOTE: reloading resets module-level state (like ACTIVE_GAMES in the
    game handlers). This only affects mid-game sessions running on the
    main bot while a new clone is being created — acceptable trade-off.
    """
    routers = []
    for mod_name in HANDLER_MODULE_NAMES:
        mod = importlib.import_module(mod_name)
        importlib.reload(mod)
        routers.append(mod.router)
    return routers


# ═══════════════════════════════════════════════
# DISPATCHER FACTORY
# ═══════════════════════════════════════════════
def build_dispatcher(bot_owner_id: int, is_clone: bool = False,
                     clone_id: int | None = None) -> Dispatcher:
    """
    Build a fully configured Dispatcher for either the main bot or a clone.
    Uses freshly-reloaded Router instances so each Dispatcher is independent.
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

    # ── Attach routers (order preserved from HANDLER_MODULE_NAMES) ──
    for router in _load_fresh_routers():
        dp.include_router(router)

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

    # ── Start membership checker ──
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
