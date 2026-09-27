from config import OWNER_ID, BOT_ADMIN_IDS


def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID


def is_bot_admin(user_id: int) -> bool:
    return user_id == OWNER_ID or user_id in BOT_ADMIN_IDS
