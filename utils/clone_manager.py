"""
utils/clone_manager.py — Spawn, manage and monitor clone bot instances.

Each clone runs its own aiogram Bot + Dispatcher in a background asyncio task
inside the same Python process as the main bot.

The dispatcher factory is injected from main.py at boot to avoid circular
imports (main imports handlers, handlers import clone_manager).
"""

import asyncio
import time
from typing import Callable, Optional

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import (
    CLONE_MEMBERSHIP_CHECK_INTERVAL, CLONE_ALLOWED_CACHE_TTL,
)
from utils import clone_db


# ═══════════════════════════════════════════════
# IN-MEMORY STATE
# ═══════════════════════════════════════════════
_active_clones: dict[int, dict] = {}
# clone_id -> {
#     "bot": Bot,
#     "task": asyncio.Task,
#     "record": asyncpg.Record,
#     "allowed_until": float,       # cache timestamp for membership check
#     "allowed": bool,
# }

_dispatcher_factory: Optional[Callable[[int], Dispatcher]] = None
_membership_task: Optional[asyncio.Task] = None


def set_dispatcher_factory(factory: Callable[[int], Dispatcher]):
    """
    Called from main.py at boot.

    The factory receives the clone's owner_user_id and returns a fully
    configured Dispatcher with all routers registered.
    """
    global _dispatcher_factory
    _dispatcher_factory = factory


# ═══════════════════════════════════════════════
# START / STOP A SINGLE CLONE
# ═══════════════════════════════════════════════
async def start_clone(clone_record) -> bool:
    """
    Start a single clone bot.

    clone_record: asyncpg.Record from clone_bots table.
    Returns True on success, False on failure.
    """
    clone_id = clone_record["id"]

    if clone_id in _active_clones:
        return True  # already running

    if _dispatcher_factory is None:
        print("❌ Clone dispatcher factory not set. Call set_dispatcher_factory() first.")
        return False

    try:
        token = clone_db.decrypt_token(clone_record["bot_token_enc"])
    except Exception as e:
        print(f"❌ Clone {clone_id}: decrypt failed — {e}")
        await clone_db.set_clone_active(clone_id, False, f"decrypt: {e}")
        return False

    try:
        bot = Bot(
            token=token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        me = await bot.get_me()
    except Exception as e:
        print(f"❌ Clone {clone_id}: get_me failed — {e}")
        await clone_db.set_clone_active(clone_id, False, f"get_me: {e}")
        return False

    # Build dispatcher with owner id injected
    try:
        dp = _dispatcher_factory(clone_record["owner_user_id"])
    except Exception as e:
        print(f"❌ Clone {clone_id}: dispatcher build failed — {e}")
        await bot.session.close()
        await clone_db.set_clone_active(clone_id, False, f"build: {e}")
        return False

    # Start polling in a background task
    task = asyncio.create_task(
        _run_polling(dp, bot, clone_id),
        name=f"clone_polling_{clone_id}",
    )

    _active_clones[clone_id] = {
        "bot": bot,
        "task": task,
        "record": clone_record,
        "allowed": True,
        "allowed_until": time.time() + CLONE_ALLOWED_CACHE_TTL,
    }

    print(f"✅ Clone #{clone_id} started → @{me.username}")
    return True


async def _run_polling(dp: Dispatcher, bot: Bot, clone_id: int):
    """Background task that runs the clone's polling loop."""
    try:
        await dp.start_polling(bot, handle_signals=False)
    except asyncio.CancelledError:
        print(f"🔌 Clone #{clone_id} polling cancelled")
    except Exception as e:
        print(f"❌ Clone #{clone_id} polling crashed — {e}")
        await clone_db.set_clone_active(clone_id, False, f"polling: {e}")
    finally:
        try:
            await bot.session.close()
        except Exception:
            pass
        _active_clones.pop(clone_id, None)


async def stop_clone(clone_id: int):
    """Stop a running clone bot."""
    info = _active_clones.pop(clone_id, None)
    if not info:
        return
    task = info["task"]
    task.cancel()
    try:
        await task
    except Exception:
        pass
    try:
        await info["bot"].session.close()
    except Exception:
        pass
    print(f"🔌 Clone #{clone_id} stopped")


async def stop_all_clones():
    """Stop every running clone. Called on shutdown."""
    for cid in list(_active_clones.keys()):
        await stop_clone(cid)


# ═══════════════════════════════════════════════
# BOOT LOADER
# ═══════════════════════════════════════════════
async def load_all_clones():
    """Load and start every active clone from the DB. Called at boot."""
    records = await clone_db.get_all_active_clones()
    if not records:
        print("ℹ️ No active clones to load")
    else:
        print(f"🚀 Loading {len(records)} active clone(s)...")

    for rec in records:
        try:
            ok = await start_clone(rec)
            if not ok:
                print(f"⚠️ Clone #{rec['id']} failed to start")
        except Exception as e:
            print(f"❌ Clone #{rec['id']} loader error — {e}")


# ═══════════════════════════════════════════════
# MEMBERSHIP CHECKER (background)
# ═══════════════════════════════════════════════
def is_clone_allowed(clone_id: int) -> bool:
    """Fast in-memory check — is this clone currently allowed to operate?"""
    info = _active_clones.get(clone_id)
    if not info:
        return False
    if time.time() > info["allowed_until"]:
        # cache expired — default to True and let the background task refresh
        return info["allowed"]
    return info["allowed"]


def get_clone_record_by_bot_id(bot_id: int):
    """Find the in-memory clone record by the bot's numeric id."""
    for cid, info in _active_clones.items():
        rec = info["record"]
        if rec["bot_id"] == bot_id:
            return rec
    return None


async def _verify_membership_for_clone(clone_record, main_bot: Bot) -> tuple[bool, list]:
    """
    Check if the clone owner is still in all required chats.
    Uses the MAIN bot to query chat membership (clones may not be in those chats).

    Returns (all_joined: bool, missing_chat_ids: list)
    """
    required = await clone_db.get_all_required_chats()
    if not required:
        return True, []

    owner_id = clone_record["owner_user_id"]
    missing = []

    for chat in required:
        chat_id = chat["chat_id"]
        try:
            member = await main_bot.get_chat_member(chat_id, owner_id)
            status = member.status
            if status in ("left", "kicked"):
                missing.append(chat_id)
        except Exception:
            # Can't check (bot not admin, or chat gone) — be lenient
            # Don't mark as missing to avoid false positives
            pass

    return len(missing) == 0, missing


async def membership_check_loop(main_bot: Bot):
    """
    Background loop: every N seconds, re-verify each active clone's owner.
    Updates the in-memory 'allowed' flag and DB is_active accordingly.
    """
    while True:
        try:
            await asyncio.sleep(CLONE_MEMBERSHIP_CHECK_INTERVAL)

            if not _active_clones:
                continue

            # Snapshot current clones
            for clone_id, info in list(_active_clones.items()):
                rec = info["record"]
                try:
                    allowed, missing = await _verify_membership_for_clone(rec, main_bot)
                except Exception as e:
                    print(f"⚠️ Membership check error for clone #{clone_id}: {e}")
                    continue

                prev = info["allowed"]
                info["allowed"] = allowed
                info["allowed_until"] = time.time() + CLONE_ALLOWED_CACHE_TTL

                if prev != allowed:
                    print(
                        f"{'✅' if allowed else '🚫'} Clone #{clone_id} "
                        f"membership → {'ALLOWED' if allowed else 'BLOCKED'} "
                        f"(missing: {missing})"
                    )

        except asyncio.CancelledError:
            print("🔌 Membership check loop stopped")
            return
        except Exception as e:
            print(f"⚠️ Membership loop error: {e}")


def start_membership_checker(main_bot: Bot):
    """Start the background membership verification loop."""
    global _membership_task
    if _membership_task is None or _membership_task.done():
        _membership_task = asyncio.create_task(
            membership_check_loop(main_bot),
            name="clone_membership_checker",
        )
        print("🔄 Clone membership checker started")


async def stop_membership_checker():
    global _membership_task
    if _membership_task:
        _membership_task.cancel()
        try:
            await _membership_task
        except Exception:
            pass
        _membership_task = None
