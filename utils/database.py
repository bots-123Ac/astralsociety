import aiosqlite
import random
import string
from datetime import datetime, timedelta
from config import DB_PATH, COINS_PER_GEM


def _gen_astral_id():
    return "".join(random.choices(string.digits, k=6))


def _now():
    return datetime.utcnow()


def _to_str(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else None


def _parse(s):
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    except Exception:
        return None


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        # ═══ USERS ═══
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT, first_name TEXT,
                astral_id TEXT UNIQUE,
                coins INTEGER DEFAULT 2000,
                gems INTEGER DEFAULT 0,
                xp INTEGER DEFAULT 0,
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

        # ═══ STUDY ═══
        await db.execute("""
            CREATE TABLE IF NOT EXISTS study_materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_name TEXT, section TEXT, subject TEXT, chapter TEXT,
                content_type TEXT, content TEXT, caption TEXT,
                uploaded_by INTEGER, uploaded_at TEXT
            )
        """)

        # ═══ POWERS ═══
        await db.execute("""
            CREATE TABLE IF NOT EXISTS powers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER, power_type TEXT, expires_at TEXT
            )
        """)

        # ═══ MISSION ═══
        await db.execute("""
            CREATE TABLE IF NOT EXISTS mission_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER, date TEXT,
                quizzes_required INTEGER,
                quiz_done INTEGER DEFAULT 0,
                pyq_downloaded INTEGER DEFAULT 0,
                claimed INTEGER DEFAULT 0
            )
        """)

        # ═══ ACTIVE GROUPS (for /start tracking) ═══
        await db.execute("""
            CREATE TABLE IF NOT EXISTS active_groups (
                chat_id INTEGER PRIMARY KEY,
                title TEXT,
                added_at TEXT
            )
        """)

        # ═══ QUIZ QUESTIONS (5000+) ═══
        await db.execute("""
            CREATE TABLE IF NOT EXISTS quiz_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                question TEXT UNIQUE,
                option_a TEXT, option_b TEXT,
                option_c TEXT, option_d TEXT,
                correct TEXT,
                created_at TEXT
            )
        """)
        await db.execute("CREATE INDEX IF NOT EXISTS idx_quiz_cat ON quiz_questions(category)")

        await db.commit()

        # ═══ SEED BUNDLED QUESTIONS ON FIRST RUN ═══
        async with db.execute("SELECT COUNT(*) FROM quiz_questions") as cur:
            cnt = (await cur.fetchone())[0]
        if cnt == 0:
            try:
                from utils.quiz_seed import QUIZ_SEED
                for cat, questions in QUIZ_SEED.items():
                    for q, a, b, c, d, correct in questions:
                        try:
                            await db.execute(
                                """INSERT OR IGNORE INTO quiz_questions
                                (category, question, option_a, option_b, option_c, option_d, correct, created_at)
                                VALUES (?,?,?,?,?,?,?,?)""",
                                (cat, q, a, b, c, d, correct, _to_str(_now()))
                            )
                        except Exception:
                            pass
                await db.commit()
            except Exception as e:
                print(f"⚠️ Seed failed: {e}")


# ═══════════════════════════════════════════════
# USERS
# ═══════════════════════════════════════════════
async def get_or_create_user(user_id, username, first_name):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM users WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
        if not row:
            astral_id = _gen_astral_id()
            while True:
                async with db.execute("SELECT 1 FROM users WHERE astral_id=?", (astral_id,)) as cur:
                    if not await cur.fetchone():
                        break
                astral_id = _gen_astral_id()
            await db.execute(
                "INSERT INTO users (user_id, username, first_name, astral_id, created_at) VALUES (?,?,?,?,?)",
                (user_id, username or "", first_name or "", astral_id, _to_str(_now()))
            )
            await db.commit()
        else:
            await db.execute(
                "UPDATE users SET username=?, first_name=? WHERE user_id=?",
                (username or "", first_name or "", user_id)
            )
            await db.commit()
        async with db.execute("SELECT * FROM users WHERE user_id=?", (user_id,)) as cur:
            return await cur.fetchone()


async def get_user_by_astral_id(astral_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM users WHERE astral_id=?", (astral_id,)) as cur:
            return await cur.fetchone()


async def get_user_by_username(username):
    username = username.lstrip("@").lower()
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM users WHERE LOWER(username)=?", (username,)) as cur:
            return await cur.fetchone()


async def add_coins(user_id, amount):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET coins = coins + ? WHERE user_id=?", (amount, user_id))
        await db.commit()


async def add_gems(user_id, amount):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET gems = gems + ? WHERE user_id=?", (amount, user_id))
        await db.commit()


async def add_xp(user_id, amount):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET xp = xp + ? WHERE user_id=?", (amount, user_id))
        await db.commit()


async def get_user_coins(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT coins FROM users WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
        return row[0] if row else 0


async def convert_coins_to_gems(user_id, coins_amount):
    if coins_amount < COINS_PER_GEM:
        return False, "min"
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT coins FROM users WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
        if not row or row[0] < coins_amount:
            return False, "insufficient"
        gems = coins_amount // COINS_PER_GEM
        await db.execute(
            "UPDATE users SET coins = coins - ?, gems = gems + ? WHERE user_id=?",
            (gems * COINS_PER_GEM, gems, user_id)
        )
        await db.commit()
    return True, gems


# ═══════════════════════════════════════════════
# PREMIUM
# ═══════════════════════════════════════════════
async def is_premium(user_id) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT premium_until FROM users WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
    if not row or not row[0]:
        return False
    return _parse(row[0]) > _now()


async def set_premium(user_id, days):
    until = _now() + timedelta(days=days)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET premium_until=? WHERE user_id=?", (_to_str(until), user_id))
        await db.commit()
    return until


async def get_premium_status(user_id):
    """Return (is_active, expires_at_str, days_left)."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT premium_until FROM users WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
    if not row or not row[0]:
        return False, None, 0
    dt = _parse(row[0])
    if not dt or dt <= _now():
        return False, None, 0
    days_left = max(0, (dt - _now()).days)
    return True, row[0], days_left


async def deduct_gems(user_id, amount) -> bool:
    """Deduct gems if user has enough. Returns True on success."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT gems FROM users WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
        if not row or row[0] < amount:
            return False
        await db.execute("UPDATE users SET gems = gems - ? WHERE user_id=?", (amount, user_id))
        await db.commit()
    return True


# ═══════════════════════════════════════════════
# SHIELD
# ═══════════════════════════════════════════════
async def is_shielded(user_id) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT shield_until FROM users WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
    if not row or not row[0]:
        return False
    return _parse(row[0]) > _now()


async def set_shield(user_id, days):
    until = _now() + timedelta(days=days)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET shield_until=? WHERE user_id=?", (_to_str(until), user_id))
        await db.commit()
    return until


async def shield_remaining(user_id) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT shield_until FROM users WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
    if not row or not row[0]:
        return 0
    dt = _parse(row[0])
    if not dt or dt <= _now():
        return 0
    return max(0, (dt - _now()).days)


# ═══════════════════════════════════════════════
# DAILY
# ═══════════════════════════════════════════════
async def can_claim_daily(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT last_daily, streak FROM users WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
    if not row:
        return True, 0
    last, streak = row
    if not last:
        return True, 0
    last_dt = _parse(last)
    today = _now().date()
    if last_dt.date() == today:
        return False, streak
    if (today - last_dt.date()).days == 1:
        return True, (streak or 0) + 1
    return True, 1


async def mark_daily_claimed(user_id, new_streak):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET last_daily=?, streak=? WHERE user_id=?",
            (_to_str(_now()), new_streak, user_id)
        )
        await db.commit()


# ═══════════════════════════════════════════════
# STATS
# ═══════════════════════════════════════════════
async def inc_quiz_attempt(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET quiz_attempted = quiz_attempted + 1 WHERE user_id=?", (user_id,))
        await db.commit()


async def inc_quiz_solved(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET quiz_solved = quiz_solved + 1 WHERE user_id=?", (user_id,))
        await db.commit()


async def inc_word_attempt(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET word_attempted = word_attempted + 1 WHERE user_id=?", (user_id,))
        await db.commit()


async def inc_word_solved(user_id, score):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET word_solved = word_solved + 1, word_score = word_score + ? WHERE user_id=?",
            (score, user_id)
        )
        await db.commit()


async def inc_number_attempt(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET number_attempted = number_attempted + 1 WHERE user_id=?", (user_id,))
        await db.commit()


async def inc_number_guess(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET number_guess = number_guess + 1 WHERE user_id=?", (user_id,))
        await db.commit()


# ═══════════════════════════════════════════════
# LEADERBOARD
# ═══════════════════════════════════════════════
async def get_global_leaderboard(limit=10):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT first_name, username, astral_id, coins FROM users ORDER BY coins DESC LIMIT ?", (limit,)
        ) as cur:
            return await cur.fetchall()


async def get_user_rank(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT coins FROM users WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
        if not row:
            return None
        async with db.execute("SELECT COUNT(*) FROM users WHERE coins > ?", (row[0],)) as cur:
            ahead = (await cur.fetchone())[0]
    return ahead + 1


# ═══════════════════════════════════════════════
# POWERS
# ═══════════════════════════════════════════════
async def add_power(user_id, power_type, days):
    until = _now() + timedelta(days=days)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO powers (user_id, power_type, expires_at) VALUES (?,?,?)",
            (user_id, power_type, _to_str(until))
        )
        await db.commit()
    return until


async def get_active_powers(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT power_type, expires_at FROM powers WHERE user_id=? AND expires_at > ?",
            (user_id, _to_str(_now()))
        ) as cur:
            return await cur.fetchall()


async def has_xp_boost(user_id) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT 1 FROM powers WHERE user_id=? AND power_type='xp_boost' AND expires_at > ? LIMIT 1",
            (user_id, _to_str(_now()))
        ) as cur:
            return (await cur.fetchone()) is not None


# ═══════════════════════════════════════════════
# MISSION
# ═══════════════════════════════════════════════
async def get_or_create_mission(user_id):
    today = _now().strftime("%Y-%m-%d")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT * FROM mission_log WHERE user_id=? AND date=?", (user_id, today)
        ) as cur:
            row = await cur.fetchone()
        if row:
            return row
        req = random.randint(0, 5)
        await db.execute(
            "INSERT INTO mission_log (user_id, date, quizzes_required) VALUES (?,?,?)",
            (user_id, today, req)
        )
        await db.commit()
        async with db.execute(
            "SELECT * FROM mission_log WHERE user_id=? AND date=?", (user_id, today)
        ) as cur:
            return await cur.fetchone()


async def mission_quiz_done(user_id, count):
    today = _now().strftime("%Y-%m-%d")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE mission_log SET quiz_done=quiz_done+? WHERE user_id=? AND date=?",
            (count, user_id, today)
        )
        await db.commit()


async def mission_pyq_done(user_id):
    today = _now().strftime("%Y-%m-%d")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE mission_log SET pyq_downloaded=1 WHERE user_id=? AND date=?",
            (user_id, today)
        )
        await db.commit()


async def mission_claim(user_id):
    today = _now().strftime("%Y-%m-%d")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE mission_log SET claimed=1 WHERE user_id=? AND date=?",
            (user_id, today)
        )
        await db.commit()


# ═══════════════════════════════════════════════
# STUDY
# ═══════════════════════════════════════════════
async def save_study_material(class_name, section, subject, chapter,
                              content_type, content, caption, uploaded_by):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO study_materials
            (class_name, section, subject, chapter, content_type, content, caption, uploaded_by, uploaded_at)
            VALUES (?,?,?,?,?,?,?,?,?)""",
            (class_name, section, subject, chapter, content_type, content,
             caption, uploaded_by, _to_str(_now()))
        )
        await db.commit()


async def get_study_chapters(class_name, section):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT DISTINCT chapter FROM study_materials WHERE class_name=? AND section=?",
            (class_name, section)
        ) as cur:
            return [r[0] for r in await cur.fetchall()]


async def get_study_materials(class_name, section, chapter):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT content_type, content, caption FROM study_materials WHERE class_name=? AND section=? AND chapter=?",
            (class_name, section, chapter)
        ) as cur:
            return await cur.fetchall()


# ═══════════════════════════════════════════════
# ACTIVE GROUPS
# ═══════════════════════════════════════════════
async def register_group(chat_id, title):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO active_groups (chat_id, title, added_at) VALUES (?,?,?)
               ON CONFLICT(chat_id) DO UPDATE SET title=?""",
            (chat_id, title or "", _to_str(_now()), title or "")
        )
        await db.commit()


async def get_all_active_groups():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT chat_id FROM active_groups") as cur:
            return [r[0] for r in await cur.fetchall()]


# ═══════════════════════════════════════════════
# QUIZ QUESTIONS (5000+)
# ═══════════════════════════════════════════════
async def add_quiz_question(category, question, correct, wrongs):
    if len(wrongs) < 3:
        return False
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT 1 FROM quiz_questions WHERE question=?", (question,)
        ) as cur:
            if await cur.fetchone():
                return False

        options = list(wrongs[:3]) + [correct]
        random.shuffle(options)
        correct_letter = "ABCD"[options.index(correct)]

        try:
            await db.execute(
                """INSERT INTO quiz_questions
                (category, question, option_a, option_b, option_c, option_d, correct, created_at)
                VALUES (?,?,?,?,?,?,?,?)""",
                (category, question, options[0], options[1], options[2], options[3],
                 correct_letter, _to_str(_now()))
            )
            await db.commit()
            return True
        except Exception:
            return False


async def get_random_quiz_question(category):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """SELECT id, question, option_a, option_b, option_c, option_d, correct
               FROM quiz_questions WHERE category=?
               ORDER BY RANDOM() LIMIT 1""",
            (category,)
        ) as cur:
            return await cur.fetchone()


async def get_quiz_count():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM quiz_questions") as cur:
            return (await cur.fetchone())[0]
