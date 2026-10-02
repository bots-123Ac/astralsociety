import time
import platform
from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from config import BOT_NAME, OWNER_IDS
from utils.permissions import is_bot_admin
from utils.database import get_pool

router = Router()

# ═══════════════════════════════════════════════
# UPTIME TRACKING
# ═══════════════════════════════════════════════
BOT_START_TIME = time.time()


def get_uptime() -> str:
    elapsed = int(time.time() - BOT_START_TIME)
    days = elapsed // 86400
    hours = (elapsed % 86400) // 3600
    minutes = (elapsed % 3600) // 60
    seconds = elapsed % 60
    parts = []
    if days: parts.append(f"{days}ᴅ")
    if hours: parts.append(f"{hours}ʜ")
    if minutes: parts.append(f"{minutes}ᴍ")
    parts.append(f"{seconds}s")
    return " ".join(parts)


# ═══════════════════════════════════════════════
# DB DEEP ANALYTICS
# ═══════════════════════════════════════════════
async def get_db_analytics() -> dict:
    pool = await get_pool()
    stats = {}

    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    today = datetime.utcnow().strftime("%Y-%m-%d")
    week_cutoff = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
    month_cutoff = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")

    # ─── Users ───
    stats["total_users"] = await pool.fetchval("SELECT COUNT(*) FROM users") or 0

    # Premium count (DB users)
    db_premium = await pool.fetchval(
        "SELECT COUNT(*) FROM users WHERE premium_until IS NOT NULL AND premium_until > $1",
        now_str
    ) or 0

    # Add owner count (owners are always premium - runtime check)
    owner_count = 0
    try:
        owner_count = len(OWNER_IDS)
        # Optionally: only count owners that exist in users table
        if OWNER_IDS:
            placeholders = ",".join(f"${i+1}" for i in range(len(OWNER_IDS)))
            existing_owners = await pool.fetchval(
                f"SELECT COUNT(*) FROM users WHERE user_id IN ({placeholders})",
                *OWNER_IDS
            )
            # Add owners not already in db_premium
            owner_count = existing_owners or 0
    except Exception:
        pass

    stats["premium_users"] = db_premium + owner_count
    stats["db_premium_users"] = db_premium
    stats["owner_count"] = owner_count

    stats["shielded_users"] = await pool.fetchval(
        "SELECT COUNT(*) FROM users WHERE shield_until IS NOT NULL AND shield_until > $1",
        now_str
    ) or 0

    # ─── Activity ───
    stats["daily_active"] = await pool.fetchval(
        "SELECT COUNT(DISTINCT user_id) FROM user_activity WHERE activity_date = $1",
        today
    ) or 0
    stats["weekly_active"] = await pool.fetchval(
        "SELECT COUNT(DISTINCT user_id) FROM user_activity WHERE activity_date >= $1",
        week_cutoff
    ) or 0
    stats["monthly_active"] = await pool.fetchval(
        "SELECT COUNT(DISTINCT user_id) FROM user_activity WHERE activity_date >= $1",
        month_cutoff
    ) or 0

    # ─── Economy ───
    stats["total_coins"] = await pool.fetchval("SELECT COALESCE(SUM(coins), 0) FROM users") or 0
    stats["total_gems"] = await pool.fetchval("SELECT COALESCE(SUM(gems), 0) FROM users") or 0
    stats["total_xp"] = await pool.fetchval("SELECT COALESCE(SUM(xp), 0) FROM users") or 0
    stats["avg_coins"] = int(stats["total_coins"] / stats["total_users"]) if stats["total_users"] else 0

    # ─── Quiz ───
    stats["quiz_count"] = await pool.fetchval("SELECT COUNT(*) FROM quiz_questions") or 0

    rows = await pool.fetch(
        "SELECT category, COUNT(*) AS c FROM quiz_questions GROUP BY category ORDER BY c DESC"
    )
    stats["quiz_by_category"] = [(r["category"], r["c"]) for r in rows]

    # ─── Study Materials ───
    stats["total_materials"] = await pool.fetchval("SELECT COUNT(*) FROM study_materials") or 0

    rows = await pool.fetch(
        "SELECT class_name, COUNT(*) AS c FROM study_materials GROUP BY class_name ORDER BY class_name"
    )
    stats["materials_by_class"] = [(r["class_name"], r["c"]) for r in rows]

    rows = await pool.fetch(
        "SELECT class_name, section, COUNT(*) AS c FROM study_materials GROUP BY class_name, section ORDER BY class_name, section"
    )
    stats["materials_by_section"] = [(r["class_name"], r["section"], r["c"]) for r in rows]

    # ─── Game Stats ───
    stats["total_quiz_attempts"] = await pool.fetchval("SELECT COALESCE(SUM(quiz_attempted), 0) FROM users") or 0
    stats["total_quiz_solved"] = await pool.fetchval("SELECT COALESCE(SUM(quiz_solved), 0) FROM users") or 0
    stats["total_number_attempts"] = await pool.fetchval("SELECT COALESCE(SUM(number_attempted), 0) FROM users") or 0
    stats["total_number_guesses"] = await pool.fetchval("SELECT COALESCE(SUM(number_guess), 0) FROM users") or 0

    # ─── Groups (FIX) ───
    stats["total_groups"] = await pool.fetchval("SELECT COUNT(*) FROM active_groups") or 0

    # ─── Top users ───
    top_rows = await pool.fetch(
        "SELECT first_name, coins FROM users ORDER BY coins DESC LIMIT 5"
    )
    stats["top_users"] = [(r["first_name"], r["coins"]) for r in top_rows]

    # ─── Top premium users ───
    prem_rows = await pool.fetch(
        """SELECT first_name, premium_until FROM users
           WHERE premium_until IS NOT NULL AND premium_until > $1
           ORDER BY premium_until DESC LIMIT 5""",
        now_str
    )
    stats["top_premium"] = [(r["first_name"], r["premium_until"]) for r in prem_rows]

    return stats


# ═══════════════════════════════════════════════
# /botstatus — ADMIN ONLY
# ═══════════════════════════════════════════════
@router.message(Command("botstatus"))
async def cmd_botstatus(message: Message):
    if not is_bot_admin(message.from_user.id):
        return await message.reply("❌ sᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")

    loading = await message.reply("⏳ <i>ᴄᴏʟʟᴇᴄᴛɪɴɢ ꜱᴛᴀᴛꜱ...</i>")

    # Ping test
    start = time.time()
    try:
        s = await get_db_analytics()
        db_ping = int((time.time() - start) * 1000)
        db_status = "✅ ᴏɴʟɪɴᴇ"
    except Exception as e:
        await loading.edit_text(f"❌ ᴅᴀᴛᴀʙᴀꜱᴇ ᴇʀʀᴏʀ:\n<code>{e}</code>")
        return

    uptime = get_uptime()
    python_ver = platform.python_version()

    lines = [
        f"📊 <b>{BOT_NAME} — ʙᴏᴛ ꜱᴛᴀᴛᴜꜱ</b>",
        f"━━━━━━━━━━━━━━━━━━━━━",
        f"",
        f"<b>⚙️ ꜱʏꜱᴛᴇᴍ:</b>",
        f"• ꜱᴛᴀᴛᴜꜱ    : ✅ ʀᴜɴɴɪɴɢ",
        f"• ᴜᴘᴛɪᴍᴇ   : <b>{uptime}</b>",
        f"• ᴅʙ ᴘɪɴɢ   : <b>{db_ping}ᴍꜱ</b>",
        f"• ᴅʙ ꜱᴛᴀᴛᴜꜱ : {db_status}",
        f"• ᴘʏᴛʜᴏɴ    : <b>{python_ver}</b>",
        f"",
        f"<b>👥 ᴜꜱᴇʀꜱ:</b>",
        f"• ᴛᴏᴛᴀʟ         : <b>{s['total_users']:,}</b>",
        f"• ᴅᴀɪʟʏ ᴀᴄᴛɪᴠᴇ  : <b>{s['daily_active']:,}</b>",
        f"• ᴡᴇᴇᴋʟʏ ᴀᴄᴛɪᴠᴇ : <b>{s['weekly_active']:,}</b>",
        f"• ᴍᴏɴᴛʜʟʏ ᴀᴄᴛɪᴠᴇ: <b>{s['monthly_active']:,}</b>",
        f"• ᴘʀᴇᴍɪᴜᴍ      : <b>{s['premium_users']:,}</b>",
        f"• ꜱʜɪᴇʟᴅᴇᴅ     : <b>{s['shielded_users']:,}</b>",
        f"• ɢʀᴏᴜᴘꜱ       : <b>{s['total_groups']:,}</b>",
        f"",
        f"<b>💰 ᴇᴄᴏɴᴏᴍʏ:</b>",
        f"• ᴛᴏᴛᴀʟ ᴄᴏɪɴꜱ : <b>{s['total_coins']:,}</b>",
        f"• ᴛᴏᴛᴀʟ ɢᴇᴍꜱ  : <b>{s['total_gems']:,}</b>",
        f"• ᴛᴏᴛᴀʟ xᴘ   : <b>{s['total_xp']:,}</b>",
        f"• ᴀᴠɢ ᴄᴏɪɴꜱ  : <b>{s['avg_coins']:,}</b>",
        f"",
        f"<b>🎮 ɢᴀᴍᴇꜱ:</b>",
        f"• ǫᴜɪᴢ ᴀᴛᴛᴇᴍᴘᴛꜱ  : <b>{s['total_quiz_attempts']:,}</b>",
        f"• ǫᴜɪᴢ ꜱᴏʟᴠᴇᴅ   : <b>{s['total_quiz_solved']:,}</b>",
        f"• ɴᴜᴍʙᴇʀ ᴀᴛᴛᴇᴍᴘᴛꜱ: <b>{s['total_number_attempts']:,}</b>",
        f"• ɴᴜᴍʙᴇʀ ɢᴜᴇꜱꜱ   : <b>{s['total_number_guesses']:,}</b>",
        f"",
        f"<b>📝 ǫᴜɪᴢ ʙᴀɴᴋ:</b>",
        f"• ᴛᴏᴛᴀʟ ǫᴜᴇꜱᴛɪᴏɴꜱ: <b>{s['quiz_count']:,}</b>",
    ]

    if s["quiz_by_category"]:
        for cat, count in s["quiz_by_category"][:8]:
            lines.append(f"  └ {cat}: <b>{count:,}</b>")

    lines += [
        f"",
        f"<b>📚 ꜱᴛᴜᴅʏ ᴍᴀᴛᴇʀɪᴀʟ:</b>",
        f"• ᴛᴏᴛᴀʟ ꜰɪʟᴇꜱ: <b>{s['total_materials']:,}</b>",
    ]

    if s["materials_by_class"]:
        for cls, count in s["materials_by_class"]:
            lines.append(f"  └ ᴄʟᴀꜱꜱ {cls}: <b>{count:,}</b> ꜰɪʟᴇꜱ")

    if s["materials_by_section"]:
        lines.append(f"")
        lines.append(f"<b>📂 ꜱᴇᴄᴛɪᴏɴ ᴡɪꜱᴇ:</b>")
        for cls, sec, count in s["materials_by_section"][:10]:
            lines.append(f"  └ {cls} — {sec}: <b>{count}</b>")

    if s["top_users"]:
        lines += [f"", f"<b>🏆 ᴛᴏᴘ 5 ʀɪᴄʜ:</b>"]
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        for i, (name, coins) in enumerate(s["top_users"]):
            lines.append(f"{medals[i]} {name}: <b>{coins:,}</b> 🪙")

    if s["top_premium"]:
        lines += [f"", f"<b>⭐ ᴛᴏᴘ ᴘʀᴇᴍɪᴜᴍ:</b>"]
        for name, until in s["top_premium"]:
            try:
                dt = datetime.strptime(until, "%Y-%m-%d %H:%M:%S")
                dt_str = dt.strftime("%d %b")
            except Exception:
                dt_str = until
            lines.append(f"  • {name} (ᴛɪʟʟ {dt_str})")

    lines += [
        f"",
        f"━━━━━━━━━━━━━━━━━━━━━",
        f"🌠 ʟᴇᴀʀɴ • ᴘʟᴀʏ • ᴄᴏᴍᴘᴇᴛᴇ • ʀɪꜱᴇ",
    ]

    final_text = "\n".join(lines)

    if len(final_text) > 4000:
        await loading.edit_text(final_text[:4000])
        await message.answer(final_text[4000:])
    else:
        await loading.edit_text(final_text)


# ═══════════════════════════════════════════════
# /users — PUBLIC
# ═══════════════════════════════════════════════
@router.message(Command("users"))
async def cmd_users(message: Message):
    pool = await get_pool()
    total = await pool.fetchval("SELECT COUNT(*) FROM users") or 0

    month_cutoff = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
    monthly = await pool.fetchval(
        "SELECT COUNT(DISTINCT user_id) FROM user_activity WHERE activity_date >= $1",
        month_cutoff
    ) or 0

    quiz = await pool.fetchval("SELECT COUNT(*) FROM quiz_questions") or 0

    await message.answer(
        f"👥 <b>ᴜꜱᴇʀ ꜱᴛᴀᴛꜱ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🌐 ᴛᴏᴛᴀʟ ᴜꜱᴇʀꜱ    : <b>{total:,}</b>\n"
        f"📅 ᴍᴏɴᴛʜʟʏ ᴀᴄᴛɪᴠᴇ : <b>{monthly:,}</b>\n"
        f"📝 ǫᴜɪᴢ ʙᴀɴᴋ    : <b>{quiz:,}</b>\n\n"
        f"🌠 ᴛʜᴀɴᴋꜱ ꜰᴏʀ ᴛʜᴇ ꜱᴜᴘᴘᴏʀᴛ!"
    )
