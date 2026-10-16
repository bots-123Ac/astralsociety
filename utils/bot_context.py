"""
utils/bot_context.py — Per-update bot identity context.

Every update (message/callback) carries the info of WHICH bot is
handling it — either the main bot or one of the clones.

Middleware sets the context, handlers read it via get_bot_context().
"""

from contextvars import ContextVar
from typing import Optional

_bot_ctx: ContextVar[Optional[dict]] = ContextVar("bot_ctx", default=None)


# ═══════════════════════════════════════════════
# SET / GET
# ═══════════════════════════════════════════════
def set_bot_context(info: dict):
    """Called by middleware before each update."""
    _bot_ctx.set(info)


def get_bot_context() -> dict:
    """
    Return the current bot's context dict. Always returns a dict
    (may be empty if nothing set). Never returns None.

    Keys (main bot):
        is_clone: bool (False)
        bot_name: str
        bot_username: str
        owner_id: int
        owner_name: str
        owner_username: str

    Keys (clone bot):
        is_clone: bool (True)
        clone_id: int
        bot_id: int
        bot_name: str
        bot_username: str
        owner_id: int
        owner_name: str
        owner_username: str
    """
    ctx = _bot_ctx.get()
    if ctx is None:
        return {}
    return ctx


def is_clone() -> bool:
    return get_bot_context().get("is_clone", False)
