"""
utils/permissions.py — Owner & admin checks with clone-awareness.

• Main bot context  → OWNER_ID + BOT_ADMIN_IDS from config
• Clone bot context → only the clone's creator is admin/owner
"""

from contextvars import ContextVar

from config import OWNER_ID, BOT_ADMIN_IDS


# ═══════════════════════════════════════════════
# BOT CONTEXT (set by middleware in main.py)
# ═══════════════════════════════════════════════
_current_bot_owner: ContextVar[int | None] = ContextVar(
    "current_bot_owner", default=None
)
_is_clone_context: ContextVar[bool] = ContextVar(
    "is_clone_context", default=False
)


def set_current_bot_context(bot_owner_id: int | None, is_clone: bool = False):
    """Called by BotContextMiddleware before each update."""
    _current_bot_owner.set(bot_owner_id)
    _is_clone_context.set(is_clone)


# ═══════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════
def is_owner(user_id: int) -> bool:
    """Is this user the OWNER of the bot currently handling the update?"""
    if _is_clone_context.get():
        # Clone bot → the clone creator is the owner
        return user_id == _current_bot_owner.get()
    # Main bot
    return user_id == OWNER_ID


def is_bot_admin(user_id: int) -> bool:
    """Is this user an admin of the bot currently handling the update?"""
    if _is_clone_context.get():
        # Clone bot → only the clone creator
        return user_id == _current_bot_owner.get()
    # Main bot
    return user_id == OWNER_ID or user_id in BOT_ADMIN_IDS


# ═══════════════════════════════════════════════
# LEGACY HELPERS (kept for backward-compat)
# ═══════════════════════════════════════════════
def is_main_bot_owner(user_id: int) -> bool:
    """Unconditionally checks the MAIN bot owner (ignores context)."""
    return user_id == OWNER_ID


def is_main_bot_admin(user_id: int) -> bool:
    """Unconditionally checks MAIN bot admins (ignores context)."""
    return user_id == OWNER_ID or user_id in BOT_ADMIN_IDS
