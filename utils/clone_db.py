"""
utils/clone_db.py — All database operations for the Clone Bot System.

Tables:
  • clone_bots         — registered clone bot tokens + owners
  • required_chats     — mandatory channels/groups
  • clone_join_cache   — cached join verification (anti rate-limit)
"""

from datetime import datetime
from typing import Optional

from cryptography.fernet import Fernet

from utils.database import get_pool, _now, _to_str


# ═══════════════════════════════════════════════
# TOKEN ENCRYPTION
# ═══════════════════════════════════════════════
def _get_fernet() -> Fernet:
    from config import CLONE_ENCRYPT_KEY
    if not CLONE_ENCRYPT_KEY:
        raise RuntimeError(
            "❌ CLONE_ENCRYPT_KEY missing! Generate with:\n"
            "   python -c \"from cryptography.fernet import Fernet; "
            "print(Fernet.generate_key().decode())\"\n"
            "   Then set it in Railway env vars."
        )
    return Fernet(CLONE_ENCRYPT_KEY.encode())


def encrypt_token(token: str) -> str:
    return _get_fernet().encrypt(token.encode()).decode()


def decrypt_token(enc: str) -> str:
    return _get_fernet().decrypt(enc.encode()).decode()


# ═══════════════════════════════════════════════
# SCHEMA
# ═══════════════════════════════════════════════
async def init_clone_tables():
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS clone_bots (
                id SERIAL PRIMARY KEY,
                owner_user_id BIGINT NOT NULL,
                owner_username TEXT,
                owner_first_name TEXT,
                bot_token_enc TEXT NOT NULL,
                bot_username TEXT UNIQUE,
                bot_name TEXT,
                bot_id BIGINT UNIQUE,
                is_active BOOLEAN DEFAULT TRUE,
                last_error TEXT,
                created_at TEXT
            )
        """)
        await conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_clone_owner_unique "
            "ON clone_bots(owner_user_id)"
        )
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_clone_active "
            "ON clone_bots(is_active)"
        )

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS required_chats (
                chat_id BIGINT PRIMARY KEY,
                chat_username TEXT,
                chat_title TEXT,
                chat_type TEXT,
                invite_link TEXT,
                added_at TEXT
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS clone_join_cache (
                user_id BIGINT PRIMARY KEY,
                last_checked TEXT,
                all_joined BOOLEAN DEFAULT FALSE,
                missing_chats TEXT
            )
        """)

    print("✅ Clone tables ready")


# ═══════════════════════════════════════════════
# REQUIRED CHATS
# ═══════════════════════════════════════════════
async def add_required_chat(chat_id: int, chat_username: Optional[str],
                            chat_title: str, chat_type: str,
                            invite_link: Optional[str] = None):
    pool = await get_pool()
    await pool.execute(
        """INSERT INTO required_chats
           (chat_id, chat_username, chat_title, chat_type, invite_link, added_at)
           VALUES ($1, $2, $3, $4, $5, $6)
           ON CONFLICT (chat_id) DO UPDATE
           SET chat_username = $2, chat_title = $3,
               chat_type = $4, invite_link = $5""",
        chat_id, chat_username, chat_title, chat_type, invite_link,
        _to_str(_now())
    )


async def remove_required_chat(chat_id: int) -> bool:
    pool = await get_pool()
    result = await pool.execute(
        "DELETE FROM required_chats WHERE chat_id = $1", chat_id
    )
    return result.endswith(" 1")


async def get_all_required_chats():
    pool = await get_pool()
    return await pool.fetch("SELECT * FROM required_chats ORDER BY added_at")


async def get_required_chats_count() -> int:
    pool = await get_pool()
    val = await pool.fetchval("SELECT COUNT(*) FROM required_chats")
    return val or 0


# ═══════════════════════════════════════════════
# JOIN CACHE
# ═══════════════════════════════════════════════
async def save_join_cache(user_id: int, all_joined: bool,
                          missing_chats: list):
    pool = await get_pool()
    missing_str = ",".join(str(c) for c in missing_chats) if missing_chats else ""
    await pool.execute(
        """INSERT INTO clone_join_cache
           (user_id, last_checked, all_joined, missing_chats)
           VALUES ($1, $2, $3, $4)
           ON CONFLICT (user_id) DO UPDATE
           SET last_checked = $2, all_joined = $3, missing_chats = $4""",
        user_id, _to_str(_now()), all_joined, missing_str
    )


async def get_join_cache(user_id: int):
    pool = await get_pool()
    return await pool.fetchrow(
        "SELECT * FROM clone_join_cache WHERE user_id = $1", user_id
    )


# ═══════════════════════════════════════════════
# CLONE BOTS — CRUD
# ═══════════════════════════════════════════════
async def create_clone(
    owner_user_id: int,
    owner_username: Optional[str],
    owner_first_name: Optional[str],
    bot_token: str,
    bot_username: str,
    bot_name: str,
    bot_id: int,
) -> int:
    pool = await get_pool()
    enc = encrypt_token(bot_token)
    row = await pool.fetchrow(
        """INSERT INTO clone_bots
           (owner_user_id, owner_username, owner_first_name,
            bot_token_enc, bot_username, bot_name, bot_id,
            is_active, created_at)
           VALUES ($1, $2, $3, $4, $5, $6, $7, TRUE, $8)
           RETURNING id""",
        owner_user_id, owner_username, owner_first_name,
        enc, bot_username, bot_name, bot_id, _to_str(_now())
    )
    return row["id"]


async def update_owner_info(clone_id: int, username: Optional[str],
                            first_name: Optional[str]):
    """Refresh cached owner info from the latest Telegram data."""
    pool = await get_pool()
    await pool.execute(
        """UPDATE clone_bots
           SET owner_username = $1, owner_first_name = $2
           WHERE id = $3""",
        username, first_name, clone_id
    )


async def get_clone_by_owner(owner_user_id: int):
    pool = await get_pool()
    return await pool.fetchrow(
        "SELECT * FROM clone_bots WHERE owner_user_id = $1", owner_user_id
    )


async def get_clone_by_bot_id(bot_id: int):
    pool = await get_pool()
    return await pool.fetchrow(
        "SELECT * FROM clone_bots WHERE bot_id = $1", bot_id
    )


async def get_clone_by_username(bot_username: str):
    pool = await get_pool()
    username = bot_username.lstrip("@").lower()
    return await pool.fetchrow(
        "SELECT * FROM clone_bots WHERE LOWER(bot_username) = $1", username
    )


async def token_already_used(bot_id: int) -> bool:
    pool = await get_pool()
    val = await pool.fetchval(
        "SELECT 1 FROM clone_bots WHERE bot_id = $1", bot_id
    )
    return val is not None


async def get_all_active_clones():
    pool = await get_pool()
    return await pool.fetch(
        "SELECT * FROM clone_bots WHERE is_active = TRUE ORDER BY id"
    )


async def get_total_clones_count() -> int:
    pool = await get_pool()
    val = await pool.fetchval("SELECT COUNT(*) FROM clone_bots")
    return val or 0


async def set_clone_active(clone_id: int, active: bool,
                           error: Optional[str] = None):
    pool = await get_pool()
    await pool.execute(
        "UPDATE clone_bots SET is_active = $1, last_error = $2 WHERE id = $3",
        active, error, clone_id
    )


async def delete_clone(clone_id: int) -> bool:
    pool = await get_pool()
    result = await pool.execute(
        "DELETE FROM clone_bots WHERE id = $1", clone_id
    )
    return result.endswith(" 1")


# ═══════════════════════════════════════════════
# ALL USERS / GROUPS (for broadcast)
# ═══════════════════════════════════════════════
async def get_all_user_ids():
    pool = await get_pool()
    rows = await pool.fetch("SELECT user_id FROM users")
    return [r["user_id"] for r in rows]


async def get_all_group_ids():
    pool = await get_pool()
    rows = await pool.fetch("SELECT chat_id FROM active_groups")
    return [r["chat_id"] for r in rows]
async def remove_dead_users(user_ids: list) -> int:
    """Delete user rows for confirmed-dead accounts (bot-blocked/deleted)."""
    if not user_ids:
        return 0
    pool = await get_pool()
    result = await pool.execute(
        "DELETE FROM users WHERE user_id = ANY($1::bigint[])", user_ids
    )
    # result is like "DELETE 45"
    try:
        return int(result.split()[-1])
    except Exception:
        return 0
