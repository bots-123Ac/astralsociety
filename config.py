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

# ═══════════════════════════════════════════════
# 🌐 WEBSITE
# ═══════════════════════════════════════════════
WEBSITE_URL = "https://crazycore.vercel.app/"

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
# 👨‍💻 CREATOR CREDITS
# ═══════════════════════════════════════════════
CREATOR_1_NAME = "⏤͟͞ 𝐂𝐑𝐀𝐙𝐘 𝐁𝐎𝐘 ᭄࿐"
CREATOR_1_USERNAME = "@OfficialCrazyBoy07"
CREATOR_1_ID = 7790607144

CREATOR_2_NAME = "𝓚𝓪𝓷𝓷𝓱𝓪࿐✨🤟"
CREATOR_2_USERNAME = "@Lunar_kanha_4572"
CREATOR_2_ID = 8165863254

CREDIT_HTML = (
    f'ᴘᴏᴡᴇʀᴇᴅ ʙʏ '
    f'<a href="tg://user?id={CREATOR_1_ID}">{CREATOR_1_NAME}</a> '
    f'& '
    f'<a href="tg://user?id={CREATOR_2_ID}">{CREATOR_2_NAME}</a>'
)

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

# ═══════════════════════════════════════════════
# ⭐ PREMIUM (via Gems)
# ═══════════════════════════════════════════════
PREMIUM_PLANS = {
    "1w": {"days": 7,   "gems": 1000,   "label": "1 Week"},
    "1m": {"days": 30,  "gems": 10000,  "label": "1 Month"},
    "1y": {"days": 365, "gems": 100000, "label": "1 Year"},
}

# ═══════════════════════════════════════════════
# 🛒 SHOP — PROTECTION CHECKER PLANS
# ═══════════════════════════════════════════════
PROTECTION_CHECKER_PLANS = {
    "basic":    {"days": 7,  "gems": 30,  "label": "Basic — 7 Days"},
    "advanced": {"days": 21, "gems": 80,  "label": "Advanced — 21 Days"},
    "ultimate": {"days": 60, "gems": 150, "label": "Ultimate — 60 Days"},
}

# ═══════════════════════════════════════════════
# 🛒 SHOP — XP BOOST PLANS
# ═══════════════════════════════════════════════
XP_BOOST_PLANS = {
    "basic":    {"days": 7,  "gems": 30,  "label": "Basic — 7 Days"},
    "advanced": {"days": 21, "gems": 80,  "label": "Advanced — 21 Days"},
    "ultimate": {"days": 60, "gems": 150, "label": "Ultimate — 60 Days"},
}

# ═══════════════════════════════════════════════
# 🛒 SHOP — EXTRA PLAY
# ═══════════════════════════════════════════════
EXTRA_PLAY_PRICE = 15  # gems per extra play

# ═══════════════════════════════════════════════
# 🛒 SHOP — MYSTERY CHEST
# ═══════════════════════════════════════════════
MYSTERY_CHEST_PRICE = 30  # gems

# Reward pool with weights (higher weight = more likely)
# Every chest gives EXACTLY ONE reward (no empty outcome)
MYSTERY_CHEST_REWARDS = [
    {"type": "coins",      "amount": 12000, "label": "💰 12,000 Coins",   "weight": 15},
    {"type": "xp",         "amount": 1000,  "label": "⭐ 1,000 XP",        "weight": 20},
    {"type": "gems",       "amount": 10,    "label": "💎 10 Gems",        "weight": 20},
    {"type": "xp_boost",   "days": 2,       "label": "⚡ 2-Day XP Boost",  "weight": 15},
    {"type": "extra_play", "amount": 1,     "label": "🎟️ 1 Extra Play",   "weight": 15},
    {"type": "coins",      "amount": 2000,  "label": "💰 2,000 Coins",    "weight": 15},
]

# ═══════════════════════════════════════════════
# ⭐ XP & LEVEL SYSTEM
# ═══════════════════════════════════════════════
XP_PER_LEVEL_BASE = 1000  # Level N → N+1 requires N × 1000 XP

# Level → one-time reward
LEVEL_REWARDS = {
    2:  {"type": "coins",      "amount": 2000, "label": "💰 2,000 Coins"},
    3:  {"type": "gems",       "amount": 2,    "label": "💎 2 Gems"},
    4:  {"type": "extra_play", "amount": 1,    "label": "🎟️ 1 Extra Play"},
    5:  {"type": "xp_boost",   "days": 1,      "label": "⚡ 1-Day XP Boost"},
    10: {"type": "badge",                      "label": "👑 Special Level Badge"},
}

# Level → Title (highest matching unlocked)
LEVEL_TITLES = [
    (20, "Empire Legend"),
    (10, "Astral Master"),
    (5,  "Astral Explorer"),
    (1,  "Astral Rookie"),
]

# ═══════════════════════════════════════════════
# 👑 OWNER IDs — UNLIMITED PREMIUM
# ═══════════════════════════════════════════════
# These IDs always have Premium — no expiry, no purchase needed
OWNER_IDS = [
    7530812073,
    7790607144,
    8165863254,
]
