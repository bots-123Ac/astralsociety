import asyncio
import importlib
import logging

from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import ErrorEvent

from config import (
    BOT_TOKEN, BOT_NAME, BOT_USERNAME, OWNER_ID,
    CREATOR_1_NAME, CREATOR_1_ID, CREATOR_2_NAME, CREATOR_2_ID,
)
from utils.logger import setup_logger
from utils.database import init_db, close_pool, get_pool, log_user_activity
from utils.quiz_loader import background_load
from utils import clone_db
from utils import clone_manager
from utils.clone_middleware import CloneAccessMiddleware
from utils.bot_context import set_bot_context


# ═══════════════════════════════════════════════
# HANDLER MODULE LIST (order matters)
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
    def __init__(self, bot_info: dict):
        self.bot_info = bot_info

    async def __call__(self, handler, event, data):
        set_bot_context(self.bot_info)
        return await handler(event, data)


# ═══════════════════════════════════════════════
# FRESH ROUTER LOADER
# ═══════════════════════════════════════════════
def _load_fresh_routers():
    routers = []
    for mod_name in HANDLER_MODULE_NAMES:
        mod = importlib.import_module(mod_name)
        importlib.reload(mod)
        routers.append(mod.router)
    return routers


# ═══════════════════════════════════════════════
# DISPATCHER FACTORY
# ═══════════════════════════════════════════════
def build_dispatcher(bot_info: dict, main_bot: Bot | None = None) -> Dispatcher:
    dp = Dispatcher()

    dp.message.middleware(ActivityMiddleware())
    dp.callback_query.middleware(ActivityMiddleware())

    dp.message.middleware(BotContextMiddleware(bot_info))
    dp.callback_query.middleware(BotContextMiddleware(bot_info))

    if bot_info.get("is_clone"):
        cam = CloneAccessMiddleware(bot_info["clone_id"], main_bot)
        dp.message.middleware(cam)
        dp.callback_query.middleware(cam)

    @dp.errors()
    async def on_error(event: ErrorEvent):
        logging.error(f"⚠️ Error: {event.exception}")
        return True

    for router in _load_fresh_routers():
        dp.include_router(router)

    return dp


# ═══════════════════════════════════════════════
# MAIN BOT INFO
# ═══════════════════════════════════════════════
def _main_bot_info() -> dict:
    return {
        "is_clone": False,
        "bot_name": BOT_NAME,
        "bot_username": BOT_USERNAME,
        "owner_id": OWNER_ID,
        "owner_name": CREATOR_1_NAME,
        "owner_username": "",
        "original_owner_1_name": CREATOR_1_NAME,
        "original_owner_1_id": CREATOR_1_ID,
        "original_owner_2_name": CREATOR_2_NAME,
        "original_owner_2_id": CREATOR_2_ID,
    }


# ═══════════════════════════════════════════════
# CLONE BOT INFO
# ═══════════════════════════════════════════════
def _clone_bot_info(clone_record) -> dict:
    return {
        "is_clone": True,
        "clone_id": clone_record["id"],
        "bot_id": clone_record["bot_id"],
        "bot_name": clone_record["bot_name"] or "",
        "bot_username": clone_record["bot_username"] or "",
        "owner_id": clone_record["owner_user_id"],
        "owner_name": clone_record["owner_first_name"] or "User",
        "owner_username": clone_record["owner_username"] or "",
        "original_owner_1_name": CREATOR_1_NAME,
        "original_owner_1_id": CREATOR_1_ID,
        "original_owner_2_name": CREATOR_2_NAME,
        "original_owner_2_id": CREATOR_2_ID,
    }


# ═══════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════
async def main():
    setup_logger()
    logging.info(f"🚀 Starting {BOT_NAME} ...")

    if not BOT_TOKEN:
        raise RuntimeError("❌ BOT_TOKEN missing!")

    await init_db()
    await clone_db.init_clone_tables()
    await get_pool()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = build_dispatcher(_main_bot_info(), main_bot=bot)

    def _factory(clone_record):
        return build_dispatcher(_clone_bot_info(clone_record), main_bot=bot)

    clone_manager.set_dispatcher_factory(_factory)

    asyncio.create_task(background_load())

    await clone_manager.load_all_clones()
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
