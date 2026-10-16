"""
utils/permissions.py — Owner & admin checks with clone-awareness.
"""

from config import OWNER_ID, BOT_ADMIN_IDS
from utils.bot_context import get_bot_context


# ═══════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════
def is_owner(user_id: int) -> bool:
    """Owner of the bot currently handling this update."""
    ctx = get_bot_context()
    if ctx.get("is_clone", False):
        return user_id == ctx.get("owner_id")
    return user_id == OWNER_ID


def is_bot_admin(user_id: int) -> bool:
    """Admin of the bot currently handling this update."""
    ctx = get_bot_context()
    if ctx.get("is_clone", False):
        return user_id == ctx.get("owner_id")
    return user_id == OWNER_ID or user_id in BOT_ADMIN_IDS


# ═══════════════════════════════════════════════
# LEGACY HELPERS
# ═══════════════════════════════════════════════
def is_main_bot_owner(user_id: int) -> bool:
    return user_id == OWNER_ID


def is_main_bot_admin(user_id: int) -> bool:
    return user_id == OWNER_ID or user_id in BOT_ADMIN_IDS
