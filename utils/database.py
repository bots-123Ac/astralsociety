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
            CREATE TABLE IF NOT EXISTS study_materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                education_type TEXT,
                class_name TEXT,
                subject TEXT,
                chapter TEXT,
                file_id TEXT,
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


async def get_or_create_user(user_id: int, username: str, first_name: str):
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


async def add_coins(user_id: int, amount: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET coins = coins + ? WHERE user_id=?", (amount, user_id))
        await db.commit()


async def add_points(user_id: int, amount: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET points = points + ? WHERE user_id=?", (amount, user_id))
        await db.commit()


async def get_balance(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT coins, points FROM users WHERE user_id=?", (user_id,)) as cur:
            return await cur.fetchone()


async def save_material(category, education_type, class_name, subject, chapter, file_id, caption, uploaded_by):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO study_materials 
            (category, education_type, class_name, subject, chapter, file_id, caption, uploaded_by)
            VALUES (?,?,?,?,?,?,?,?)""",
            (category, education_type, class_name, subject, chapter, file_id, caption, uploaded_by)
        )
        await db.commit()


async def get_materials(category, education_type, class_name, subject, chapter):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """SELECT file_id, caption FROM study_materials 
            WHERE category=? AND education_type=? AND class_name=? 
            AND subject=? AND chapter=?""",
            (category, education_type, class_name, subject, chapter)
        ) as cur:
            return await cur.fetchall()


async def save_game_score(user_id: int, game: str, score: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO game_scores (user_id, game, score) VALUES (?,?,?)",
            (user_id, game, score)
        )
        await db.commit()


async def get_leaderboard(game: str, limit: int = 10):
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
