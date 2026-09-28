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

BOT_ADD_LINK = f"https://t.me/{BOT_USERNAME.lstrip('@')}?startgroup=true"

# ═══ OWNER & ADMINS ═══
OWNER_ID = -1004398879964
BOT_ADMIN_IDS = [7748285403, 7415480513, 8165863254, 7790607144, 8987845745]

# ═══ CREATOR CREDITS ═══
CREATOR_1_NAME = "⏤͟͞ 𝐂𝐑𝐀𝐙𝐘 𝐁𝐎𝐘 ᭄࿐"
CREATOR_1_LINK = "https://t.me/OfficialCrazyBoy07"
CREATOR_2_NAME = "𝓚𝓪𝓷𝓱𝓪࿐✨🤟"
CREATOR_2_LINK = "https://t.me/Lunar_kanha_4572"

CREDIT_HTML = (
    f'ᴘᴏᴡᴇʀᴇᴅ ʙʏ '
    f'<a href="{CREATOR_1_LINK}">{CREATOR_1_NAME}</a> '
    f'& '
    f'<a href="{CREATOR_2_LINK}">{CREATOR_2_NAME}</a>'
)

DB_PATH = os.getenv("DB_PATH", "astral.db")

# ═══ ECONOMY ═══
COINS_PER_GEM = 100
DAILY_NORMAL_COINS = 2000
DAILY_NORMAL_XP = 150
DAILY_PREMIUM_COINS = 5500
DAILY_PREMIUM_XP = 350
MISSION_REWARD_COINS = 8000
MISSION_REWARD_XP = 200
QUIZ_REWARD_COINS = 40
NUMBER_REWARD_COINS = 80
WORD_MAX_REWARD = 100
ROB_NORMAL_PERCENT = 10
ROB_PREMIUM_PERCENT = 5
SHIELD_FREE_DAYS = 2
GIVE_DEDUCTION_PERCENT = 10

# ═══ EVENT SETTINGS (automatic, no admin command needed) ═══
# 3600 = 1 hour (production). Change to 60 for testing (1 min).
EVENT_INTERVAL_SECONDS = 3600
EVENT_TIME_LIMIT_MINUTES = 60
EVENT_PRIZE_MIN = 500
EVENT_PRIZE_MAX = 2000
EVENT_NUMBER_MIN = 100
EVENT_NUMBER_MAX = 500
EVENT_MAX_GUESSES = 10
EVENT_MAX_WINS_PER_DAY = 3

PREMIUM_PLANS = {
    "1m": {"days": 30, "stars": 90},
    "4m": {"days": 120, "stars": 140},
    "12m": {"days": 365, "stars": 175},
}
