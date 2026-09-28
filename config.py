import os
from dotenv import load_dotenv

load_dotenv()

# ═══════════════════════════════════════════════
# 🤖 BOT IDENTITY
# ═══════════════════════════════════════════════
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
BOT_NAME = "˹𝐀𝐬𝐭𝐫𝐚𝐥 ꭙ 𝐄𝐦𝐩𝐢𝐫𝐞˼"
BOT_USERNAME = "@AstralEmpireRobot"

# ═══════════════════════════════════════════════
# 📢 SUPPORT LINKS
# ═══════════════════════════════════════════════
SUPPORT_GROUP_NAME = "『𓆩𝓐𝓼𝓽𝓻𝓪𝓵 𝓢𝓸𝓬𝓲𝓮𝓽𝔂𓆪』✨🚀🔭"
SUPPORT_GROUP_LINK = "https://t.me/+-j8FiVjAUXExMmM1"
SUPPORT_CHANNEL_NAME = "˹𝐀𝐬𝐭𝐫𝐚𝐥 ꭙ 𝐒𝐭𝐮𝐝𝐲 𝐂𝐡𝐞𝐬𝐭˼"
SUPPORT_CHANNEL_LINK = "https://t.me/Astral_study_chest"

BOT_ADD_LINK = f"https://t.me/{BOT_USERNAME.lstrip('@')}?startgroup=true"

# ═══════════════════════════════════════════════
# 👑 OWNER & ADMINS
# ═══════════════════════════════════════════════
OWNER_ID = -1004398879964

BOT_ADMIN_IDS = [
    7748285403,
    7415480513,
    8165863254,
    7790607144,
    8987845745,
]

# ═══════════════════════════════════════════════
# 👨‍💻 CREATOR CREDITS (ID-based, no preview card)
# ═══════════════════════════════════════════════
CREATOR_1_NAME = "⏤͟͞ 𝐂𝐑𝐀𝐙𝐘 𝐁𝐎𝐘 ᭄࿐"
CREATOR_1_USERNAME = "@OfficialCrazyBoy07"
CREATOR_1_ID = 7790607144

CREATOR_2_NAME = "𝓚𝓪𝓷𝓱𝓪࿐✨🤟"
CREATOR_2_USERNAME = "@Lunar_kanha_4572"
CREATOR_2_ID = 8165863254

CREDIT_HTML = (
    f'ᴘᴏᴡᴇʀᴇᴅ ʙʏ '
    f'<a href="tg://user?id={CREATOR_2_ID}">{CREATOR_2_NAME}</a>'
    f'& '
    f'<a href="https://t.me/OfficialCrazyBoy07">{CREATOR_1_NAME}</a> '
}

# ═══════════════════════════════════════════════
# 🗄️ DATABASE — Neon PostgreSQL
# ═══════════════════════════════════════════════
DATABASE_URL = os.getenv("DATABASE_URL", "")

# ═══════════════════════════════════════════════
# 💰 ECONOMY
# ═══════════════════════════════════════════════
COINS_PER_GEM = 100
DAILY_NORMAL_COINS = 2000
DAILY_NORMAL_XP = 150
DAILY_PREMIUM_COINS = 5000
DAILY_PREMIUM_XP = 350
MISSION_REWARD_COINS = 8000
MISSION_REWARD_XP = 200
QUIZ_REWARD_COINS = 40
NUMBER_REWARD_COINS = 80
NUMBER_MIN = 100
NUMBER_MAX = 500
NUMBER_MAX_ATTEMPTS = 12
ROB_NORMAL_PERCENT = 10
ROB_PREMIUM_PERCENT = 5
GIVE_DEDUCTION_PERCENT = 10
SHIELD_NORMAL_MAX_DAYS = 2
SHIELD_PREMIUM_MAX_DAYS = 5

PREMIUM_PLANS = {
    "1w": {"days": 7,   "gems": 1000,   "label": "1 Week"},
    "1m": {"days": 30,  "gems": 10000,  "label": "1 Month"},
    "1y": {"days": 365, "gems": 100000, "label": "1 Year"},
}

XP_BOOST_PLANS = {
    5:  {"gems": 6,  "label": "5 Days"},
    7:  {"gems": 8,  "label": "7 Days"},
    12: {"gems": 13, "label": "12 Days"},
}
PROTECTION_CHECKER_COST = 6
