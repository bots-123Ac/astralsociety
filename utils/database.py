import os
import time
import random
import string
from datetime import datetime, timedelta

import asyncpg

from config import (
    DATABASE_URL, COINS_PER_GEM,
    LEVEL_REWARDS, LEVEL_TITLES, XP_PER_LEVEL_BASE,
)


# ═══════════════════════════════════════════════
# CONNECTION POOL
# ═══════════════════════════════════════════════
_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        if not DATABASE_URL:
            raise RuntimeError("❌ DATABASE_URL missing!")
        _pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=3, max_size=20,
            command_timeout=15,
            statement_cache_size=100,
            max_inactive_connection_lifetime=300,
        )
        async with _pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        print("✅ PostgreSQL pool warmed up")
    return _pool


async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


# ═══════════════════════════════════════════════
# IN-MEMORY CACHE
# ═══════════════════════════════════════════════
CACHE_TTL = 5

_premium_cache: dict = {}
_shield_cache: dict = {}
_coins_cache: dict = {}


def _cache_get(cache: dict, key):
    entry = cache.get(key)
    if entry is None:
        return None
    value, expires = entry
    if time.time() > expires:
        cache.pop(key, None)
        return None
    return value


def _cache_set(cache: dict, key, value):
    cache[key] = (value, time.time() + CACHE_TTL)


def _cache_invalidate(cache: dict, key):
    cache.pop(key, None)


# ═══════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════
def _gen_astral_id():
    return "".join(random.choices(string.digits, k=6))


def _now():
    return datetime.utcnow()


def _to_str(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else None


def _parse(s):
    if not s:
        return None
    if isinstance(s, datetime):
        return s
    try:
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    except Exception:
        try:
            return datetime.strptime(s, "%Y-%m-%d")
        except Exception:
            return None


# ═══════════════════════════════════════════════
# LEVEL MATH
# ═══════════════════════════════════════════════
def xp_for_next_level(level: int) -> int:
    return level * XP_PER_LEVEL_BASE


def cumulative_xp_for_level(level: int) -> int:
    if level <= 1:
        return 0
    return XP_PER_LEVEL_BASE * (level - 1) * level // 2


def compute_level_from_xp(total_xp: int) -> int:
    if total_xp < 0:
        total_xp = 0
    level = 1
    while cumulative_xp_for_level(level + 1) <= total_xp:
        level += 1
        if level > 9999:
            break
    return level


def compute_level_progress(total_xp: int, level: int):
    current_threshold = cumulative_xp_for_level(level)
    xp_in_level = total_xp - current_threshold
    xp_needed = xp_for_next_level(level)
    if xp_in_level < 0:
        xp_in_level = 0
    return xp_in_level, xp_needed


def progress_bar(current: int, needed: int, length: int = 10) -> str:
    if needed <= 0:
        return "▰" * length
    filled = int((current / needed) * length)
    filled = max(0, min(length, filled))
    return "▰" * filled + "░" * (length - filled)


def get_level_title(level: int) -> str:
    for lvl, title in LEVEL_TITLES:
        if level >= lvl:
            return title
    return "Astral Rookie"


def format_level_up_message(info: dict) -> str:
    rewards_text = ""
    if info.get("rewards"):
        rewards_text = "\n" + "\n".join(
            f"🎁 ʟᴇᴠᴇʟ {lvl}: {r['label']}" for lvl, r in info["rewards"]
        )
    bar = progress_bar(info["xp_in_level"], info["xp_needed"])
    title = info.get("title", "")
    return (
        f"🎉 <b>ʟᴇᴠᴇʟ ᴜᴘ!</b> 🎉\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⭐ ʏᴏᴜ ʀᴇᴀᴄʜᴇᴅ <b>ʟᴇᴠᴇʟ {info['new_level']}</b>!\n"
        f"👑 ᴛɪᴛʟᴇ: <b>{title}</b>"
        f"{rewards_text}\n\n"
        f"⚡ xᴘ: <b>{info['xp_in_level']:,} / {info['xp_needed']:,}</b>\n"
        f"<code>{bar}</code>\n\n"
        f"ᴋᴇᴇᴘ ɢᴏɪɴɢ, ᴀꜱᴛʀᴀʟ ʟᴇɢᴇɴᴅ! 🚀"
    )


# ═══════════════════════════════════════════════
# INIT DB
# ═══════════════════════════════════════════════
async def init_db():
    pool = await get_pool()

    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username TEXT, first_name TEXT,
                astral_id TEXT UNIQUE,
                coins BIGINT DEFAULT 2000,
                gems BIGINT DEFAULT 0,
                xp BIGINT DEFAULT 0,
                level INTEGER DEFAULT 1,
                level_rewards_claimed TEXT DEFAULT '',
                custom_emoji TEXT DEFAULT '',
                quiz_attempted INTEGER DEFAULT 0,
                quiz_solved INTEGER DEFAULT 0,
                word_attempted INTEGER DEFAULT 0,
                word_solved INTEGER DEFAULT 0,
                word_score INTEGER DEFAULT 0,
                number_attempted INTEGER DEFAULT 0,
                number_guess INTEGER DEFAULT 0,
                premium_until TEXT,
                shield_until TEXT,
                last_daily TEXT,
                streak INTEGER DEFAULT 0,
                created_at TEXT
            )
        """)

        # ═══ SAFE MIGRATIONS ═══
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS level INTEGER DEFAULT 1")
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS level_rewards_claimed TEXT DEFAULT ''")
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS custom_emoji TEXT DEFAULT ''")

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS study_materials (
                id SERIAL PRIMARY KEY,
                class_name TEXT, section TEXT, subject TEXT, chapter TEXT,
                content_type TEXT, content TEXT, caption TEXT,
                uploaded_by BIGINT, uploaded_at TEXT
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS powers (
                id SERIAL PRIMARY KEY,
                user_id BIGINT, power_type TEXT, expires_at TEXT
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS mission_log (
                id SERIAL PRIMARY KEY,
                user_id BIGINT, date TEXT,
                quizzes_required INTEGER, quiz_done INTEGER DEFAULT 0,
                pyq_downloaded INTEGER DEFAULT 0, claimed INTEGER DEFAULT 0
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS active_groups (
                chat_id BIGINT PRIMARY KEY, title TEXT, added_at TEXT
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS quiz_questions (
                id SERIAL PRIMARY KEY,
                category TEXT, question TEXT UNIQUE,
                option_a TEXT, option_b TEXT, option_c TEXT, option_d TEXT,
                correct TEXT, created_at TEXT
            )
        """)
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_quiz_cat ON quiz_questions(category)")

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_activity (
                user_id BIGINT, activity_date TEXT,
                PRIMARY KEY (user_id, activity_date)
            )
        """)
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_activity_date ON user_activity(activity_date)")

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS treasure_plays (
                user_id BIGINT, play_date TEXT, count INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, play_date)
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS luckydoor_plays (
                user_id BIGINT, play_date TEXT, count INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, play_date)
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS bombdefuse_plays (
                user_id BIGINT, play_date TEXT, count INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, play_date)
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS extra_plays (
                user_id BIGINT PRIMARY KEY, count INTEGER DEFAULT 0
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS coin_transactions (
                id SERIAL PRIMARY KEY, user_id BIGINT,
                amount BIGINT, created_at TEXT
            )
        """)
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_ct_user ON coin_transactions(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_ct_created ON coin_transactions(created_at)")

    # ═══ SEED QUIZ ═══
    cnt = await get_quiz_count()
    if cnt == 0:
        try:
            from utils.quiz_seed import QUIZ_SEED
            print("📚 Seeding quiz questions...")
            async with pool.acquire() as conn:
                for cat, questions in QUIZ_SEED.items():
                    for q, a, b, c, d, correct in questions:
                        try:
                            await conn.execute(
                                """INSERT INTO quiz_questions
                                (category, question, option_a, option_b,
                                 option_c, option_d, correct, created_at)
                                VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
                                ON CONFLICT (question) DO NOTHING""",
                                cat, q, a, b, c, d, correct, _to_str(_now())
                            )
                        except Exception:
                            pass
            print(f"✅ Seeded {await get_quiz_count()} questions")
        except Exception as e:
            print(f"⚠️ Seed failed: {e}")


# ═══════════════════════════════════════════════
# USERS
# ═══════════════════════════════════════════════
async def get_or_create_user(user_id, username, first_name):
    pool = await get_pool()
    row = await pool.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
    if not row:
        astral_id = _gen_astral_id()
        while await pool.fetchval("SELECT 1 FROM users WHERE astral_id=$1", astral_id):
            astral_id = _gen_astral_id()
        await pool.execute(
            """INSERT INTO users (user_id,username,first_name,astral_id,created_at)
               VALUES ($1,$2,$3,$4,$5)""",
            user_id, username or "", first_name or "", astral_id, _to_str(_now())
        )
    else:
        try:
            await pool.execute(
                "UPDATE users SET username=$1, first_name=$2 WHERE user_id=$3",
                username or "", first_name or "", user_id
            )
        except Exception:
            pass
    return await pool.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)


async def get_user_by_astral_id(aid):
    pool = await get_pool()
    return await pool.fetchrow("SELECT * FROM users WHERE astral_id=$1", aid)


async def get_user_by_username(u):
    pool = await get_pool()
    u = u.lstrip("@").lower()
    return await pool.fetchrow("SELECT * FROM users WHERE LOWER(username)=$1", u)


async def get_user_by_id(uid):
    pool = await get_pool()
    return await pool.fetchrow("SELECT * FROM users WHERE user_id=$1", uid)


async def add_coins(user_id, amount, is_earning=True):
    pool = await get_pool()
    await pool.execute(
        "UPDATE users SET coins = coins + $1 WHERE user_id = $2", amount, user_id
    )
    _cache_invalidate(_coins_cache, user_id)
    if is_earning and amount > 0:
        try:
            await pool.execute(
                "INSERT INTO coin_transactions (user_id,amount,created_at) VALUES ($1,$2,$3)",
                user_id, amount, _to_str(_now())
            )
        except Exception:
            pass


async def add_gems(user_id, amount):
    pool = await get_pool()
    await pool.execute("UPDATE users SET gems = gems + $1 WHERE user_id = $2", amount, user_id)


async def add_xp(user_id, amount):
    if amount <= 0:
        return None
    pool = await get_pool()
    await pool.execute("UPDATE users SET xp = xp + $1 WHERE user_id = $2", amount, user_id)
    row = await pool.fetchrow(
        "SELECT xp, level, level_rewards_claimed FROM users WHERE user_id=$1", user_id
    )
    if not row:
        return None
    total_xp = row["xp"] or 0
    current_level = row["level"] or 1
    claimed_raw = row["level_rewards_claimed"] or ""
    claimed = set()
    for p in claimed_raw.split(","):
        p = p.strip()
        if p.isdigit():
            claimed.add(int(p))
    new_level = compute_level_from_xp(total_xp)
    if new_level <= current_level:
        return None
    new_claims = list(claimed)
    rewards_granted = []
    for lvl in range(current_level + 1, new_level + 1):
        reward = LEVEL_REWARDS.get(lvl)
        if not reward or lvl in claimed:
            continue
        rtype = reward["type"]
        if rtype == "coins":
            await pool.execute(
                "UPDATE users SET coins = coins + $1 WHERE user_id = $2",
                reward["amount"], user_id
            )
            _cache_invalidate(_coins_cache, user_id)
            try:
                await pool.execute(
                    "INSERT INTO coin_transactions (user_id,amount,created_at) VALUES ($1,$2,$3)",
                    user_id, reward["amount"], _to_str(_now())
                )
            except Exception:
                pass
        elif rtype == "gems":
            await pool.execute(
                "UPDATE users SET gems = gems + $1 WHERE user_id = $2",
                reward["amount"], user_id
            )
        elif rtype == "extra_play":
            await add_extra_play(user_id, reward["amount"])
        elif rtype == "xp_boost":
            await pool.execute(
                "INSERT INTO powers (user_id,power_type,expires_at) VALUES ($1,$2,$3)",
                user_id, "xp_boost", _to_str(_now() + timedelta(days=reward["days"]))
            )
        new_claims.append(lvl)
        rewards_granted.append((lvl, reward))
    new_claimed_str = ",".join(str(x) for x in sorted(set(new_claims)))
    await pool.execute(
        "UPDATE users SET level=$1, level_rewards_claimed=$2 WHERE user_id=$3",
        new_level, new_claimed_str, user_id
    )
    xp_in_level, xp_needed = compute_level_progress(total_xp, new_level)
    return {
        "new_level": new_level, "old_level": current_level,
        "total_xp": total_xp, "xp_in_level": xp_in_level,
        "xp_needed": xp_needed, "rewards": rewards_granted,
        "title": get_level_title(new_level),
    }


async def get_user_coins(user_id) -> int:
    c = _cache_get(_coins_cache, user_id)
    if c is not None:
        return c
    pool = await get_pool()
    val = await pool.fetchval("SELECT coins FROM users WHERE user_id=$1", user_id)
    r = val if val is not None else 0
    _cache_set(_coins_cache, user_id, r)
    return r


async def get_user_gems(user_id) -> int:
    pool = await get_pool()
    val = await pool.fetchval("SELECT gems FROM users WHERE user_id=$1", user_id)
    return val if val is not None else 0


async def convert_coins_to_gems(user_id, coins_amount):
    if coins_amount < COINS_PER_GEM:
        return False, "min"
    pool = await get_pool()
    cur = await pool.fetchval("SELECT coins FROM users WHERE user_id=$1", user_id)
    if cur is None or cur < coins_amount:
        return False, "insufficient"
    gems = coins_amount // COINS_PER_GEM
    cost = gems * COINS_PER_GEM
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute("UPDATE users SET coins = coins - $1 WHERE user_id=$2", cost, user_id)
            await conn.execute("UPDATE users SET gems = gems + $1 WHERE user_id=$2", gems, user_id)
    _cache_invalidate(_coins_cache, user_id)
    return True, gems


# ═══════════════════════════════════════════════
# PREMIUM
# ═══════════════════════════════════════════════
async def is_premium(user_id) -> bool:
    # ═══ OWNER CHECK — always premium ═══
    try:
        from config import OWNER_IDS
        if user_id in OWNER_IDS:
            return True
    except Exception as e:
        print(f"⚠️ Owner check failed: {e}")

    cached = _cache_get(_premium_cache, user_id)
    if cached is not None:
        return cached
    pool = await get_pool()
    val = await pool.fetchval("SELECT premium_until FROM users WHERE user_id=$1", user_id)
    result = False
    if val:
        dt = _parse(val)
        if dt and dt > _now():
            result = True
    _cache_set(_premium_cache, user_id, result)
    return result


async def set_premium(user_id, days):
    until = _now() + timedelta(days=days)
    pool = await get_pool()
    await pool.execute(
        "UPDATE users SET premium_until=$1 WHERE user_id=$2", _to_str(until), user_id
    )
    _cache_invalidate(_premium_cache, user_id)
    return until


async def get_premium_status(user_id):
    pool = await get_pool()
    val = await pool.fetchval("SELECT premium_until FROM users WHERE user_id=$1", user_id)
    if not val:
        return False, None, 0
    dt = _parse(val)
    if not dt or dt <= _now():
        return False, None, 0
    return True, val, max(0, (dt - _now()).days)


async def deduct_gems(user_id, amount) -> bool:
    pool = await get_pool()
    cur = await pool.fetchval("SELECT gems FROM users WHERE user_id=$1", user_id)
    if cur is None or cur < amount:
        return False
    await pool.execute("UPDATE users SET gems = gems - $1 WHERE user_id=$2", amount, user_id)
    return True


# ═══════════════════════════════════════════════
# SHIELD
# ═══════════════════════════════════════════════
async def is_shielded(user_id) -> bool:
    c = _cache_get(_shield_cache, user_id)
    if c is not None:
        return c
    pool = await get_pool()
    val = await pool.fetchval("SELECT shield_until FROM users WHERE user_id=$1", user_id)
    result = False
    if val:
        dt = _parse(val)
        if dt and dt > _now():
            result = True
    _cache_set(_shield_cache, user_id, result)
    return result


async def set_shield(user_id, days):
    until = _now() + timedelta(days=days)
    pool = await get_pool()
    await pool.execute(
        "UPDATE users SET shield_until=$1 WHERE user_id=$2", _to_str(until), user_id
    )
    _cache_invalidate(_shield_cache, user_id)
    return until


async def shield_remaining(user_id) -> int:
    pool = await get_pool()
    val = await pool.fetchval("SELECT shield_until FROM users WHERE user_id=$1", user_id)
    if not val:
        return 0
    dt = _parse(val)
    if not dt or dt <= _now():
        return 0
    return max(0, (dt - _now()).days)


async def shield_remaining_seconds(user_id) -> int:
    pool = await get_pool()
    val = await pool.fetchval("SELECT shield_until FROM users WHERE user_id=$1", user_id)
    if not val:
        return 0
    dt = _parse(val)
    if not dt or dt <= _now():
        return 0
    return max(0, int((dt - _now()).total_seconds()))


def format_shield_time(total_seconds: int) -> str:
    if total_seconds <= 0:
        return "0ᴅ 0ʜ 0ᴍ 0ꜱ"
    d = total_seconds // 86400
    h = (total_seconds % 86400) // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    return f"{d}ᴅ {h}ʜ {m}ᴍ {s}ꜱ"


# ═══════════════════════════════════════════════
# DAILY
# ═══════════════════════════════════════════════
async def can_claim_daily(user_id):
    pool = await get_pool()
    row = await pool.fetchrow(
        "SELECT last_daily, streak FROM users WHERE user_id=$1", user_id
    )
    if not row:
        return True, 0
    last = row["last_daily"]
    streak = row["streak"]
    if not last:
        return True, 0
    dt = _parse(last)
    if not dt:
        return True, 1
    today = _now().date()
    if dt.date() == today:
        return False, streak or 0
    if (today - dt.date()).days == 1:
        return True, (streak or 0) + 1
    return True, 1


async def mark_daily_claimed(user_id, s):
    pool = await get_pool()
    await pool.execute(
        "UPDATE users SET last_daily=$1, streak=$2 WHERE user_id=$3",
        _to_str(_now()), s, user_id
    )


# ═══════════════════════════════════════════════
# STATS
# ═══════════════════════════════════════════════
async def inc_quiz_attempt(u):
    pool = await get_pool()
    await pool.execute("UPDATE users SET quiz_attempted = quiz_attempted + 1 WHERE user_id=$1", u)


async def inc_quiz_solved(u):
    pool = await get_pool()
    await pool.execute("UPDATE users SET quiz_solved = quiz_solved + 1 WHERE user_id=$1", u)


async def inc_word_attempt(u):
    pool = await get_pool()
    await pool.execute("UPDATE users SET word_attempted = word_attempted + 1 WHERE user_id=$1", u)


async def inc_word_solved(u, score):
    pool = await get_pool()
    await pool.execute(
        "UPDATE users SET word_solved = word_solved + 1, word_score = word_score + $1 WHERE user_id=$2",
        score, u
    )


async def inc_number_attempt(u):
    pool = await get_pool()
    await pool.execute("UPDATE users SET number_attempted = number_attempted + 1 WHERE user_id=$1", u)


async def inc_number_guess(u):
    pool = await get_pool()
    await pool.execute("UPDATE users SET number_guess = number_guess + 1 WHERE user_id=$1", u)


# ═══════════════════════════════════════════════
# LEADERBOARD
# ═══════════════════════════════════════════════
def _today_start():
    return _now().replace(hour=0, minute=0, second=0, microsecond=0)


def _week_start():
    t = _now().replace(hour=0, minute=0, second=0, microsecond=0)
    return t - timedelta(days=t.weekday())


def _month_start():
    return _now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _period_start(period: str):
    if period == "today":
        return _today_start()
    if period == "weekly":
        return _week_start()
    if period == "monthly":
        return _month_start()
    return None


async def get_leaderboard(period: str = "alltime", limit: int = 10):
    pool = await get_pool()
    if period == "alltime":
        return await pool.fetch(
            """SELECT first_name, username, astral_id, coins, custom_emoji
               FROM users WHERE coins > 0
               ORDER BY coins DESC LIMIT $1""", limit
        )
    since = _period_start(period)
    if since is None:
        return []
    return await pool.fetch(
        """SELECT u.first_name, u.username, u.astral_id,
                  u.custom_emoji,
                  SUM(t.amount)::BIGINT AS coins
           FROM coin_transactions t
           JOIN users u ON u.user_id = t.user_id
           WHERE t.created_at >= $1
           GROUP BY u.user_id, u.first_name, u.username, u.astral_id, u.custom_emoji
           HAVING SUM(t.amount) > 0
           ORDER BY coins DESC LIMIT $2""",
        _to_str(since), limit
    )


async def get_user_leaderboard_rank(user_id: int, period: str = "alltime"):
    pool = await get_pool()
    if period == "alltime":
        coins = await pool.fetchval("SELECT coins FROM users WHERE user_id=$1", user_id)
        if not coins or coins <= 0:
            return None
        ahead = await pool.fetchval("SELECT COUNT(*) FROM users WHERE coins > $1", coins)
        return (ahead or 0) + 1
    since = _period_start(period)
    if since is None:
        return None
    my = await pool.fetchval(
        """SELECT COALESCE(SUM(amount),0) FROM coin_transactions
           WHERE user_id=$1 AND created_at >= $2""",
        user_id, _to_str(since)
    )
    if not my or my <= 0:
        return None
    ahead = await pool.fetchval(
        """SELECT COUNT(*) FROM (
            SELECT user_id, SUM(amount) AS s FROM coin_transactions
            WHERE created_at >= $1 GROUP BY user_id HAVING SUM(amount) > $2
        ) AS sub""", _to_str(since), my
    )
    return (ahead or 0) + 1


async def get_user_period_balance(user_id: int, period: str = "alltime") -> int:
    pool = await get_pool()
    if period == "alltime":
        val = await pool.fetchval("SELECT coins FROM users WHERE user_id=$1", user_id)
        return val or 0
    since = _period_start(period)
    if since is None:
        return 0
    val = await pool.fetchval(
        """SELECT COALESCE(SUM(amount),0) FROM coin_transactions
           WHERE user_id=$1 AND created_at >= $2""",
        user_id, _to_str(since)
    )
    return val or 0


async def get_global_leaderboard(limit=10):
    return await get_leaderboard("alltime", limit)


async def get_user_rank(user_id):
    return await get_user_leaderboard_rank(user_id, "alltime")


# ═══════════════════════════════════════════════
# LEVEL HELPERS
# ═══════════════════════════════════════════════
async def get_user_level(user_id):
    pool = await get_pool()
    row = await pool.fetchrow("SELECT xp, level FROM users WHERE user_id=$1", user_id)
    if not row:
        return 1, 0, XP_PER_LEVEL_BASE, "Astral Rookie"
    total_xp = row["xp"] or 0
    level = row["level"] or compute_level_from_xp(total_xp)
    xp_in_level, xp_needed = compute_level_progress(total_xp, level)
    return level, xp_in_level, xp_needed, get_level_title(level)


# ═══════════════════════════════════════════════
# EXTRA PLAYS
# ═══════════════════════════════════════════════
async def get_extra_plays(user_id) -> int:
    pool = await get_pool()
    val = await pool.fetchval("SELECT count FROM extra_plays WHERE user_id=$1", user_id)
    return val or 0


async def add_extra_play(user_id, amount=1):
    pool = await get_pool()
    row = await pool.fetchrow("SELECT count FROM extra_plays WHERE user_id=$1", user_id)
    if not row:
        await pool.execute(
            "INSERT INTO extra_plays (user_id,count) VALUES ($1,$2)", user_id, amount
        )
    else:
        await pool.execute(
            "UPDATE extra_plays SET count = count + $1 WHERE user_id=$2", amount, user_id
        )


async def use_extra_play(user_id) -> bool:
    pool = await get_pool()
    row = await pool.fetchrow("SELECT count FROM extra_plays WHERE user_id=$1", user_id)
    if not row or (row["count"] or 0) <= 0:
        return False
    await pool.execute(
        "UPDATE extra_plays SET count = count - 1 WHERE user_id=$1", user_id
    )
    return True


# ═══════════════════════════════════════════════
# GAME PLAY CONSUMPTION
# ═══════════════════════════════════════════════
async def try_play_game(user_id, get_plays_fn, daily_limit: int):
    """
    Returns (allowed: bool, used_extra: bool, plays_left: int)
    """
    plays = await get_plays_fn(user_id)
    if plays < daily_limit:
        return True, False, daily_limit - plays
    used = await use_extra_play(user_id)
    if used:
        return True, True, 0
    return False, False, 0


# ═══════════════════════════════════════════════
# CUSTOM EMOJI
# ═══════════════════════════════════════════════
async def set_custom_emoji(user_id, emoji: str):
    pool = await get_pool()
    await pool.execute(
        "UPDATE users SET custom_emoji = $1 WHERE user_id = $2", emoji, user_id
    )


async def get_custom_emoji(user_id) -> str:
    pool = await get_pool()
    val = await pool.fetchval("SELECT custom_emoji FROM users WHERE user_id=$1", user_id)
    return val or ""


# ═══════════════════════════════════════════════
# POWERS
# ═══════════════════════════════════════════════
async def add_power(user_id, power_type, days):
    until = _now() + timedelta(days=days)
    pool = await get_pool()
    await pool.execute(
        "INSERT INTO powers (user_id,power_type,expires_at) VALUES ($1,$2,$3)",
        user_id, power_type, _to_str(until)
    )
    return until


async def get_active_powers(user_id):
    pool = await get_pool()
    return await pool.fetch(
        "SELECT power_type, expires_at FROM powers WHERE user_id=$1 AND expires_at>$2",
        user_id, _to_str(_now())
    )


async def has_xp_boost(user_id) -> bool:
    pool = await get_pool()
    v = await pool.fetchval(
        """SELECT 1 FROM powers WHERE user_id=$1 AND power_type='xp_boost'
           AND expires_at > $2 LIMIT 1""",
        user_id, _to_str(_now())
    )
    return v is not None


async def has_protection_checker(user_id) -> bool:
    pool = await get_pool()
    v = await pool.fetchval(
        """SELECT 1 FROM powers WHERE user_id=$1 AND power_type='protection_checker'
           AND expires_at > $2 LIMIT 1""",
        user_id, _to_str(_now())
    )
    return v is not None


# ═══════════════════════════════════════════════
# MISSION
# ═══════════════════════════════════════════════
async def get_or_create_mission(user_id):
    today = _now().strftime("%Y-%m-%d")
    pool = await get_pool()
    row = await pool.fetchrow(
        "SELECT * FROM mission_log WHERE user_id=$1 AND date=$2", user_id, today
    )
    if row:
        return row
    req = random.randint(0, 5)
    await pool.execute(
        "INSERT INTO mission_log (user_id,date,quizzes_required) VALUES ($1,$2,$3)",
        user_id, today, req
    )
    return await pool.fetchrow(
        "SELECT * FROM mission_log WHERE user_id=$1 AND date=$2", user_id, today
    )


async def mission_quiz_done(user_id, count):
    today = _now().strftime("%Y-%m-%d")
    pool = await get_pool()
    await pool.execute(
        "UPDATE mission_log SET quiz_done = quiz_done + $1 WHERE user_id=$2 AND date=$3",
        count, user_id, today
    )


async def mission_pyq_done(user_id):
    today = _now().strftime("%Y-%m-%d")
    pool = await get_pool()
    await pool.execute(
        "UPDATE mission_log SET pyq_downloaded = 1 WHERE user_id=$1 AND date=$2",
        user_id, today
    )


async def mission_claim(user_id):
    today = _now().strftime("%Y-%m-%d")
    pool = await get_pool()
    await pool.execute(
        "UPDATE mission_log SET claimed = 1 WHERE user_id=$1 AND date=$2",
        user_id, today
    )


# ═══════════════════════════════════════════════
# STUDY
# ═══════════════════════════════════════════════
async def save_study_material(class_name, section, subject, chapter,
                              content_type, content, caption, uploaded_by):
    pool = await get_pool()
    await pool.execute(
        """INSERT INTO study_materials
        (class_name,section,subject,chapter,content_type,content,caption,uploaded_by,uploaded_at)
        VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)""",
        class_name, section, subject, chapter, content_type, content,
        caption, uploaded_by, _to_str(_now())
    )


async def get_study_chapters(class_name, section):
    pool = await get_pool()
    rows = await pool.fetch(
        "SELECT DISTINCT chapter FROM study_materials WHERE class_name=$1 AND section=$2",
        class_name, section
    )
    return [r["chapter"] for r in rows]


async def get_study_materials(class_name, section, chapter):
    pool = await get_pool()
    return await pool.fetch(
        """SELECT content_type, content, caption FROM study_materials
           WHERE class_name=$1 AND section=$2 AND chapter=$3""",
        class_name, section, chapter
    )


# ═══════════════════════════════════════════════
# ACTIVE GROUPS
# ═══════════════════════════════════════════════
async def register_group(chat_id, title):
    pool = await get_pool()
    await pool.execute(
        """INSERT INTO active_groups (chat_id,title,added_at) VALUES ($1,$2,$3)
           ON CONFLICT (chat_id) DO UPDATE SET title=$2""",
        chat_id, title or "", _to_str(_now())
    )


async def get_all_active_groups():
    pool = await get_pool()
    rows = await pool.fetch("SELECT chat_id FROM active_groups")
    return [r["chat_id"] for r in rows]


# ═══════════════════════════════════════════════
# QUIZ QUESTIONS
# ═══════════════════════════════════════════════
async def add_quiz_question(category, question, correct, wrongs):
    if len(wrongs) < 3:
        return False
    pool = await get_pool()
    exists = await pool.fetchval("SELECT 1 FROM quiz_questions WHERE question=$1", question)
    if exists:
        return False
    options = list(wrongs[:3]) + [correct]
    random.shuffle(options)
    cl = "ABCD"[options.index(correct)]
    try:
        await pool.execute(
            """INSERT INTO quiz_questions
            (category,question,option_a,option_b,option_c,option_d,correct,created_at)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8)""",
            category, question, options[0], options[1], options[2], options[3],
            cl, _to_str(_now())
        )
        return True
    except Exception:
        return False


async def get_random_quiz_question(category):
    pool = await get_pool()
    return await pool.fetchrow(
        """SELECT id, question, option_a, option_b, option_c, option_d, correct
           FROM quiz_questions WHERE category=$1 ORDER BY RANDOM() LIMIT 1""",
        category
    )


async def get_quiz_count() -> int:
    pool = await get_pool()
    v = await pool.fetchval("SELECT COUNT(*) FROM quiz_questions")
    return v or 0


# ═══════════════════════════════════════════════
# BOT STATS
# ═══════════════════════════════════════════════
async def log_user_activity(user_id):
    today = _now().strftime("%Y-%m-%d")
    pool = await get_pool()
    try:
        await pool.execute(
            """INSERT INTO user_activity (user_id,activity_date) VALUES ($1,$2)
               ON CONFLICT (user_id, activity_date) DO NOTHING""",
            user_id, today
        )
    except Exception:
        pass


async def get_total_users() -> int:
    pool = await get_pool()
    return (await pool.fetchval("SELECT COUNT(*) FROM users")) or 0


async def get_daily_active_users() -> int:
    today = _now().strftime("%Y-%m-%d")
    pool = await get_pool()
    return (await pool.fetchval(
        "SELECT COUNT(DISTINCT user_id) FROM user_activity WHERE activity_date=$1", today
    )) or 0


async def get_weekly_active_users() -> int:
    c = (_now() - timedelta(days=7)).strftime("%Y-%m-%d")
    pool = await get_pool()
    return (await pool.fetchval(
        "SELECT COUNT(DISTINCT user_id) FROM user_activity WHERE activity_date>=$1", c
    )) or 0


async def get_monthly_active_users() -> int:
    c = (_now() - timedelta(days=30)).strftime("%Y-%m-%d")
    pool = await get_pool()
    return (await pool.fetchval(
        "SELECT COUNT(DISTINCT user_id) FROM user_activity WHERE activity_date>=$1", c
    )) or 0


async def get_bot_full_stats() -> dict:
    return {
        "total_users": await get_total_users(),
        "daily_active": await get_daily_active_users(),
        "weekly_active": await get_weekly_active_users(),
        "monthly_active": await get_monthly_active_users(),
        "quiz_count": await get_quiz_count(),
    }


# ═══════════════════════════════════════════════
# TREASURE
# ═══════════════════════════════════════════════
async def get_treasure_plays(user_id) -> int:
    today = _now().strftime("%Y-%m-%d")
    pool = await get_pool()
    v = await pool.fetchval(
        "SELECT count FROM treasure_plays WHERE user_id=$1 AND play_date=$2",
        user_id, today
    )
    return v or 0


async def inc_treasure_play(user_id) -> int:
    today = _now().strftime("%Y-%m-%d")
    pool = await get_pool()
    row = await pool.fetchrow(
        "SELECT count FROM treasure_plays WHERE user_id=$1 AND play_date=$2",
        user_id, today
    )
    if not row:
        await pool.execute(
            "INSERT INTO treasure_plays (user_id,play_date,count) VALUES ($1,$2,1)",
            user_id, today
        )
        return 1
    n = (row["count"] or 0) + 1
    await pool.execute(
        "UPDATE treasure_plays SET count=$1 WHERE user_id=$2 AND play_date=$3",
        n, user_id, today
    )
    return n


# ═══════════════════════════════════════════════
# LUCKY DOOR
# ═══════════════════════════════════════════════
async def get_luckydoor_plays(user_id) -> int:
    today = _now().strftime("%Y-%m-%d")
    pool = await get_pool()
    v = await pool.fetchval(
        "SELECT count FROM luckydoor_plays WHERE user_id=$1 AND play_date=$2",
        user_id, today
    )
    return v or 0


async def inc_luckydoor_play(user_id) -> int:
    today = _now().strftime("%Y-%m-%d")
    pool = await get_pool()
    row = await pool.fetchrow(
        "SELECT count FROM luckydoor_plays WHERE user_id=$1 AND play_date=$2",
        user_id, today
    )
    if not row:
        await pool.execute(
            "INSERT INTO luckydoor_plays (user_id,play_date,count) VALUES ($1,$2,1)",
            user_id, today
        )
        return 1
    n = (row["count"] or 0) + 1
    await pool.execute(
        "UPDATE luckydoor_plays SET count=$1 WHERE user_id=$2 AND play_date=$3",
        n, user_id, today
    )
    return n


# ═══════════════════════════════════════════════
# BOMB DEFUSE
# ═══════════════════════════════════════════════
async def get_bombdefuse_plays(user_id) -> int:
    today = _now().strftime("%Y-%m-%d")
    pool = await get_pool()
    v = await pool.fetchval(
        "SELECT count FROM bombdefuse_plays WHERE user_id=$1 AND play_date=$2",
        user_id, today
    )
    return v or 0


async def inc_bombdefuse_play(user_id) -> int:
    today = _now().strftime("%Y-%m-%d")
    pool = await get_pool()
    row = await pool.fetchrow(
        "SELECT count FROM bombdefuse_plays WHERE user_id=$1 AND play_date=$2",
        user_id, today
    )
    if not row:
        await pool.execute(
            "INSERT INTO bombdefuse_plays (user_id,play_date,count) VALUES ($1,$2,1)",
            user_id, today
        )
        return 1
    n = (row["count"] or 0) + 1
    await pool.execute(
        "UPDATE bombdefuse_plays SET count=$1 WHERE user_id=$2 AND play_date=$3",
        n, user_id, today
    )
    return n
