import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
BOT_NAME = "˹𝐀𝐬𝐭𝐫𝐚𝐥 ꭙ 𝐄𝐦𝐩𝐢𝐫𝐞˼"
BOT_USERNAME = "@AstralEmpireRobot"

SUPPORT_GROUP_NAME = "『𓆩𝓐𝓼𝓽𝓻𝓪𝓵 𝓢𝓸𝓬𝓲𝓮𝓽𝔂𓆪』✨🚀🔭"
SUPPORT_GROUP_LINK = "https://t.me/+-j8FiVjAUXExMmM1"
SUPPORT_CHANNEL_NAME = "˹𝐀𝐬𝐭𝐫𝐚𝐥 ꭙ 𝐒𝐭𝐮𝐝𝐲 𝐂𝐡𝐞𝐬𝐭˼"
SUPPORT_CHANNEL_LINK = "https://t.me/Astral_study_chest"

# ═══════════════════════════════════════════════
# 👑 OWNER (Bot ka head)
# ═══════════════════════════════════════════════
OWNER_ID = 7748285403

# ═══════════════════════════════════════════════
# 👑 BOT ADMIN IDS (Study material managers)
# Ye users notes/quiz upload kar sakte hain
# ═══════════════════════════════════════════════
BOT_ADMIN_IDS = [
    7748285403,
    7415480513,
    8165863254,
    7790607144,
]

# ═══════════════════════════════════════════════
# ⚠️ GROUP ADMINS ko yahan mat daalo
# Bot Telegram se auto-detect karta hai per group
# ═══════════════════════════════════════════════

DB_PATH = os.getenv("DB_PATH", "astral.db")
