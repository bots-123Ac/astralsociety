import aiosqlite
from config import DB_PATH


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
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
        await db.execute("""
            CREATE TABLE IF NOT EXISTS study_resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                education_type TEXT,
                class_name TEXT,
                category TEXT,
                subject TEXT,
                chapter TEXT,
                resource_type TEXT,
                content_type TEXT,
                content TEXT,
                caption TEXT,
                uploaded_by INTEGER,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS game_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                game TEXT,
                score INTEGER,
                played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


# ─────────── USERS ───────────

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


async def add_coins(user_id, amount):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET coins = coins + ? WHERE user_id=?", (amount, user_id))
        await db.commit()


async def add_points(user_id, amount):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET points = points + ? WHERE user_id=?", (amount, user_id))
        await db.commit()


async def get_balance(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT coins, points FROM users WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
            return row if row else (0, 0)


async def get_user_stats(user_id):
    """Returns (coins, points, games_played, total_score)."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT coins, points FROM users WHERE user_id=?", (user_id,)
        ) as cur:
            row = await cur.fetchone()
        coins, points = (row if row else (0, 0))
        async with db.execute(
            "SELECT COUNT(*), COALESCE(SUM(score),0) FROM game_scores WHERE user_id=?",
            (user_id,)
        ) as cur:
            gp, ts = await cur.fetchone()
    return coins, points, gp or 0, ts or 0


# ─────────── STUDY ───────────

async def save_resource(education_type, class_name, category, subject,
                        chapter, resource_type, content_type, content,
                        caption, uploaded_by):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO study_resources
            (education_type, class_name, category, subject, chapter,
             resource_type, content_type, content, caption, uploaded_by)
            VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (education_type, class_name, category, subject, chapter,
             resource_type, content_type, content, caption, uploaded_by)
        )
        await db.commit()


async def get_resource_type_counts(education_type, class_name, category, subject):
    """Return list of (resource_type, count)."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """SELECT resource_type, COUNT(*) FROM study_resources
            WHERE education_type=? AND class_name=? AND category=? AND subject=?
            GROUP BY resource_type""",
            (education_type, class_name, category, subject)
        ) as cur:
            return await cur.fetchall()


async def get_chapters(education_type, class_name, category, subject, resource_type):
    """Return list of (chapter, count)."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """SELECT chapter, COUNT(*) FROM study_resources
            WHERE education_type=? AND class_name=? AND category=? AND subject=?
            AND resource_type=?
            GROUP BY chapter ORDER BY chapter""",
            (education_type, class_name, category, subject, resource_type)
        ) as cur:
            return await cur.fetchall()


async def get_resources(education_type, class_name, category, subject,
                        chapter, resource_type):
    """Return list of (content_type, content, caption)."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """SELECT content_type, content, caption FROM study_resources
            WHERE education_type=? AND class_name=? AND category=? AND subject=?
            AND chapter=? AND resource_type=?""",
            (education_type, class_name, category, subject, chapter, resource_type)
        ) as cur:
            return await cur.fetchall()


async def delete_resources(education_type, class_name, category, subject):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """DELETE FROM study_resources
            WHERE education_type=? AND class_name=? AND category=? AND subject=?""",
            (education_type, class_name, category, subject)
        )
        await db.commit()


# ─────────── GAMES ───────────

async def save_game_score(user_id, game, score):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO game_scores (user_id, game, score) VALUES (?,?,?)",
            (user_id, game, score)
        )
        await db.commit()


async def get_leaderboard(game, limit=10):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """SELECT u.first_name, u.username, MAX(g.score) as best
               FROM game_scores g JOIN users u ON u.user_id = g.user_id
               WHERE g.game = ?
               GROUP BY g.user_id
               ORDER BY best DESC LIMIT ?""",
            (game, limit)
        ) as cur:
            return await cur.fetchall()
