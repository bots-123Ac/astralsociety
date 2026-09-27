from aiogram import Bot
from aiogram.types import ChatMemberOwner, ChatMemberAdministrator

from config import OWNER_ID, BOT_ADMIN_IDS


# ═══════════════════════════════════════════════
# BOT ADMIN (Study Material Managers)
# ═══════════════════════════════════════════════
def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID


def is_bot_admin(user_id: int) -> bool:
    return user_id == OWNER_ID or user_id in BOT_ADMIN_IDS


# Backward compat
def is_admin(user_id: int) -> bool:
    return is_bot_admin(user_id)


# ═══════════════════════════════════════════════
# GROUP ADMIN (Telegram actual admins)
# ═══════════════════════════════════════════════
async def get_group_member(bot: Bot, chat_id: int, user_id: int):
    """Return ChatMember object or None."""
    try:
        return await bot.get_chat_member(chat_id, user_id)
    except Exception:
        return None


async def is_group_admin(bot: Bot, chat_id: int, user_id: int) -> bool:
    """User is owner or admin of this group."""
    member = await get_group_member(bot, chat_id, user_id)
    return isinstance(member, (ChatMemberOwner, ChatMemberAdministrator))


async def has_right(bot: Bot, chat_id: int, user_id: int, right: str) -> bool:
    """
    Check if user has specific Telegram admin right in this group.
    right: 'can_delete_messages', 'can_restrict_members',
           'can_promote_members', 'can_change_info',
           'can_invite_users', 'can_pin_messages', etc.
    """
    member = await get_group_member(bot, chat_id, user_id)
    if member is None:
        return False
    # Owner has all rights
    if isinstance(member, ChatMemberOwner):
        return True
    if isinstance(member, ChatMemberAdministrator):
        return getattr(member, right, False)
    return False
