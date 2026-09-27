import aiosqlite
from config import DB_PATH


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        # Users
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                coins INTEGER DEFAULT 100,
                points INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Study material
        await db.execute("""
            CREATE TABLE IF NOT EXISTS study_resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                board TEXT, class_name TEXT, subject TEXT,
                chapter TEXT, material_type TEXT,
                content_type TEXT, content TEXT, caption TEXT,
                uploaded_by INTEGER,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Quiz
        await db.execute("""
            CREATE TABLE IF NOT EXISTS quiz_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exam TEXT, subject TEXT, topic TEXT,
                question TEXT,
                option_a TEXT, option_b TEXT, option_c TEXT, option_d TEXT,
                correct TEXT, difficulty TEXT DEFAULT 'medium',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS quiz_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER, question_id INTEGER,
                selected TEXT, is_correct INTEGER,
                exam TEXT, subject TEXT, topic TEXT,
                attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Word game (per user per chat)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS word_games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER, chat_id INTEGER,
                word TEXT, word_length INTEGER,
                attempts INTEGER DEFAULT 0,
                max_attempts INTEGER DEFAULT 30,
                status TEXT DEFAULT 'active',
                guessed_json TEXT DEFAULT '[]',
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, chat_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS word_game_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER, word TEXT,
                attempts INTEGER, won INTEGER,
                score INTEGER,
                played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Warnings
        await db.execute("""
            CREATE TABLE IF NOT EXISTS warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER, group_id INTEGER,
                reason TEXT, warned_by INTEGER,
                warned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Group settings
        await db.execute("""
            CREATE TABLE IF NOT EXISTS group_settings (
                group_id INTEGER PRIMARY KEY,
                welcome_enabled INTEGER DEFAULT 1,
                goodbye_enabled INTEGER DEFAULT 1,
                antilink INTEGER DEFAULT 0,
                antiflood INTEGER DEFAULT 0,
                antiforward INTEGER DEFAULT 0,
                captcha INTEGER DEFAULT 0,
                welcome_text TEXT DEFAULT '',
                rules TEXT DEFAULT ''
            )
        """)
        # Group locks (per type)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS group_locks (
                group_id INTEGER, lock_type TEXT,
                is_locked INTEGER DEFAULT 0,
                PRIMARY KEY (group_id, lock_type)
            )
        """)
        await db.commit()


# ═══════════════════════════════════════════════
# USERS
# ═══════════════════════════════════════════════
async def get_or_create_user(user_id, username, first_name):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM users WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
        if not row:
            await db.execute(
                "INSERT INTO users (user_id, username, first_name) VALUES (?,?,?)",
                (user_id, username or "", first_name or "")
            )
            await db.commit()
        async with db.execute("SELECT * FROM users WHERE user_id=?", (user_id,)) as cur:
            return await cur.fetchone()


async def get_user_stats(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT coins, points FROM users WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
        coins, points = row if row else (0, 0)
        async with db.execute(
            "SELECT COUNT(*), COALESCE(SUM(is_correct),0) FROM quiz_attempts WHERE user_id=?",
            (user_id,)
        ) as cur:
            qa, qc = await cur.fetchone()
        async with db.execute(
            "SELECT COUNT(*), COALESCE(SUM(won),0), COALESCE(SUM(score),0) FROM word_game_history WHERE user_id=?",
            (user_id,)
        ) as cur:
            wg, ww, ws = await cur.fetchone()
    return {
        "coins": coins, "points": points,
        "quiz_attempted": qa or 0, "quiz_correct": qc or 0,
        "word_games": wg or 0, "word_won": ww or 0, "word_score": ws or 0,
    }


async def add_points(user_id, amount):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET points = points + ? WHERE user_id=?", (amount, user_id))
        await db.commit()


async def add_coins(user_id, amount):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET coins = coins + ? WHERE user_id=?", (amount, user_id))
        await db.commit()


# ═══════════════════════════════════════════════
# STUDY
# ═══════════════════════════════════════════════
async def save_resource(board, class_name, subject, chapter, material_type,
                       content_type, content, caption, uploaded_by):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """SELECT id FROM study_resources
               WHERE board=? AND class_name=? AND subject=? AND chapter=?
               AND material_type=? AND content=?""",
            (board, class_name, subject, chapter, material_type, content)
        ) as cur:
            if await cur.fetchone():
                return False
        await db.execute(
            """INSERT INTO study_resources
            (board, class_name, subject, chapter, material_type,
             content_type, content, caption, uploaded_by)
            VALUES (?,?,?,?,?,?,?,?,?)""",
            (board, class_name, subject, chapter, material_type,
             content_type, content, caption, uploaded_by)
        )
        await db.commit()
        return True


async def get_subjects(board, class_name):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT DISTINCT subject FROM study_resources WHERE board=? AND class_name=?",
            (board, class_name)
        ) as cur:
            return [r[0] for r in await cur.fetchall()]


async def get_chapters(board, class_name, subject):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """SELECT chapter, COUNT(*) FROM study_resources
               WHERE board=? AND class_name=? AND subject=?
               GROUP BY chapter ORDER BY chapter""",
            (board, class_name, subject)
        ) as cur:
            return await cur.fetchall()


async def get_material_types(board, class_name, subject, chapter):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """SELECT material_type, COUNT(*) FROM study_resources
               WHERE board=? AND class_name=? AND subject=? AND chapter=?
               GROUP BY material_type""",
            (board, class_name, subject, chapter)
        ) as cur:
            return await cur.fetchall()


async def get_resources(board, class_name, subject, chapter, material_type):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """SELECT content_type, content, caption FROM study_resources
               WHERE board=? AND class_name=? AND subject=? AND chapter=? AND material_type=?""",
            (board, class_name, subject, chapter, material_type)
        ) as cur:
            return await cur.fetchall()


async def get_study_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM study_resources") as cur:
            return (await cur.fetchone())[0]


# ═══════════════════════════════════════════════
# QUIZ
# ═══════════════════════════════════════════════
async def add_quiz_question(exam, subject, topic, question,
                            a, b, c, d, correct, difficulty="medium"):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO quiz_questions
            (exam, subject, topic, question, option_a, option_b, option_c, option_d, correct, difficulty)
            VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (exam, subject, topic, question, a, b, c, d, correct, difficulty)
        )
        await db.commit()


async def get_random_question(exam=None, subject=None, topic=None):
    q = "SELECT id, exam, subject, topic, question, option_a, option_b, option_c, option_d, correct FROM quiz_questions WHERE 1=1"
    p = []
    if exam:
        q += " AND exam=?"; p.append(exam)
    if subject:
        q += " AND subject=?"; p.append(subject)
    if topic:
        q += " AND topic=?"; p.append(topic)
    q += " ORDER BY RANDOM() LIMIT 1"
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(q, p) as cur:
            return await cur.fetchone()


async def save_quiz_attempt(user_id, question_id, selected, is_correct, exam, subject, topic):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO quiz_attempts
            (user_id, question_id, selected, is_correct, exam, subject, topic)
            VALUES (?,?,?,?,?,?,?)""",
            (user_id, question_id, selected, is_correct, exam, subject, topic)
        )
        await db.commit()


async def get_quiz_stats(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """SELECT COUNT(*), COALESCE(SUM(is_correct),0)
               FROM quiz_attempts WHERE user_id=?""", (user_id,)
        ) as cur:
            total, correct = await cur.fetchone()
        async with db.execute(
            """SELECT subject, COUNT(*), SUM(is_correct)
               FROM quiz_attempts WHERE user_id=?
               GROUP BY subject""", (user_id,)
        ) as cur:
            subjects = await cur.fetchall()
    return total or 0, correct or 0, subjects


# ═══════════════════════════════════════════════
# WORD GAME (per user per chat)
# ═══════════════════════════════════════════════
async def start_word_game(user_id, chat_id, word, length):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM word_games WHERE user_id=? AND chat_id=?",
            (user_id, chat_id)
        )
        await db.execute(
            """INSERT INTO word_games
            (user_id, chat_id, word, word_length, attempts, status, guessed_json)
            VALUES (?,?,?,?,0,'active','[]')""",
            (user_id, chat_id, word, length)
        )
        await db.commit()


async def get_word_game(user_id, chat_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """SELECT word, word_length, attempts, max_attempts, status, guessed_json
               FROM word_games WHERE user_id=? AND chat_id=?""",
            (user_id, chat_id)
        ) as cur:
            return await cur.fetchone()


async def update_word_game(user_id, chat_id, attempts, status, guessed_json):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """UPDATE word_games SET attempts=?, status=?, guessed_json=?
               WHERE user_id=? AND chat_id=?""",
            (attempts, status, guessed_json, user_id, chat_id)
        )
        await db.commit()


async def end_word_game(user_id, chat_id, word, attempts, won, score):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM word_games WHERE user_id=? AND chat_id=?",
            (user_id, chat_id)
        )
        await db.execute(
            """INSERT INTO word_game_history
            (user_id, word, attempts, won, score) VALUES (?,?,?,?,?)""",
            (user_id, word, attempts, 1 if won else 0, score)
        )
        await db.commit()


async def end_all_games_in_chat(chat_id):
    """End all active games in a group (admin action)."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM word_games WHERE chat_id=?", (chat_id,))
        await db.commit()


async def get_active_games_in_chat(chat_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM word_games WHERE chat_id=? AND status='active'",
            (chat_id,)
        ) as cur:
            return (await cur.fetchone())[0]


async def get_word_leaderboard(limit=10):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """SELECT u.first_name, u.username, COALESCE(SUM(h.score),0) as pts
               FROM word_game_history h JOIN users u ON u.user_id = h.user_id
               GROUP BY h.user_id ORDER BY pts DESC LIMIT ?""",
            (limit,)
        ) as cur:
            return await cur.fetchall()


# ═══════════════════════════════════════════════
# WARNINGS
# ═══════════════════════════════════════════════
async def add_warning(user_id, group_id, reason, warned_by):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO warnings (user_id, group_id, reason, warned_by) VALUES (?,?,?,?)",
            (user_id, group_id, reason, warned_by)
        )
        await db.commit()


async def get_warnings(user_id, group_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM warnings WHERE user_id=? AND group_id=?",
            (user_id, group_id)
        ) as cur:
            return (await cur.fetchone())[0]


async def remove_last_warning(user_id, group_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """SELECT id FROM warnings WHERE user_id=? AND group_id=?
               ORDER BY id DESC LIMIT 1""",
            (user_id, group_id)
        ) as cur:
            row = await cur.fetchone()
        if row:
            await db.execute("DELETE FROM warnings WHERE id=?", (row[0],))
            await db.commit()
            return True
        return False


# ═══════════════════════════════════════════════
# GROUP SETTINGS
# ═══════════════════════════════════════════════
async def get_or_create_group(group_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM group_settings WHERE group_id=?", (group_id,)) as cur:
            row = await cur.fetchone()
        if not row:
            await db.execute("INSERT INTO group_settings (group_id) VALUES (?)", (group_id,))
            await db.commit()


async def toggle_group_setting(group_id, setting):
    allowed = {"welcome_enabled", "goodbye_enabled", "antilink",
               "antiflood", "antiforward", "captcha"}
    if setting not in allowed:
        return None
    await get_or_create_group(group_id)
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(f"SELECT {setting} FROM group_settings WHERE group_id=?", (group_id,)) as cur:
            row = await cur.fetchone()
        new_val = 0 if (row and row[0]) else 1
        await db.execute(f"UPDATE group_settings SET {setting}=? WHERE group_id=?", (new_val, group_id))
        await db.commit()
        return new_val


async def get_group_setting(group_id, setting):
    await get_or_create_group(group_id)
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(f"SELECT {setting} FROM group_settings WHERE group_id=?", (group_id,)) as cur:
            row = await cur.fetchone()
        return row[0] if row else 0


# ═══════════════════════════════════════════════
# GROUP LOCKS
# ═══════════════════════════════════════════════
LOCK_TYPES = ["stickers", "gifs", "photos", "videos", "documents",
              "links", "audio", "voice", "polls", "games", "contacts", "forwards"]


async def set_lock(group_id, lock_type, locked: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO group_locks (group_id, lock_type, is_locked)
               VALUES (?,?,?)
               ON CONFLICT(group_id, lock_type) DO UPDATE SET is_locked=?""",
            (group_id, lock_type, locked, locked)
        )
        await db.commit()


async def get_lock(group_id, lock_type) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT is_locked FROM group_locks WHERE group_id=? AND lock_type=?",
            (group_id, lock_type)
        ) as cur:
            row = await cur.fetchone()
        return row[0] if row else 0


async def get_all_locks(group_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT lock_type, is_locked FROM group_locks WHERE group_id=?",
            (group_id,)
        ) as cur:
            return dict(await cur.fetchall())
