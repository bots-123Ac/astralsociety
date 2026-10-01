"""
XP & Level System for Astral Empire
"""

# ═══════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════
XP_PER_LEVEL_BASE = 1000  # Level × 1000

# Level → Reward (given ONCE per level)
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
# LEVEL MATH
# ═══════════════════════════════════════════════
def xp_for_next_level(level: int) -> int:
    """XP required to go from `level` → `level + 1`."""
    return level * XP_PER_LEVEL_BASE


def cumulative_xp_for_level(level: int) -> int:
    """Total lifetime XP needed to REACH the given level."""
    if level <= 1:
        return 0
    # Sum: 1000 * (1 + 2 + ... + (level-1))
    return XP_PER_LEVEL_BASE * (level - 1) * level // 2


def compute_level_from_xp(total_xp: int) -> int:
    """Given lifetime total XP, return current level."""
    if total_xp < 0:
        total_xp = 0
    level = 1
    while cumulative_xp_for_level(level + 1) <= total_xp:
        level += 1
        if level > 9999:  # safety
            break
    return level


def compute_level_progress(total_xp: int, level: int):
    """Return (xp_in_current_level, xp_needed_for_next)."""
    current_threshold = cumulative_xp_for_level(level)
    xp_in_level = total_xp - current_threshold
    xp_needed = xp_for_next_level(level)
    if xp_in_level < 0:
        xp_in_level = 0
    return xp_in_level, xp_needed


def progress_bar(current: int, needed: int, length: int = 10) -> str:
    """Return unicode progress bar like ▰▰▰▰▰▰░░░░"""
    if needed <= 0:
        return "▰" * length
    filled = int((current / needed) * length)
    filled = max(0, min(length, filled))
    return "▰" * filled + "░" * (length - filled)


def get_level_title(level: int) -> str:
    """Return highest matching title."""
    for lvl, title in LEVEL_TITLES:
        if level >= lvl:
            return title
    return "Astral Rookie"


# ═══════════════════════════════════════════════
# MESSAGE FORMATTERS
# ═══════════════════════════════════════════════
def format_level_up_message(info: dict) -> str:
    """Format the level-up notification."""
    rewards_text = ""
    if info.get("rewards"):
        rewards_text = "\n".join(
            f"🎁 ʟᴇᴠᴇʟ {lvl}: {r['label']}" for lvl, r in info["rewards"]
        )
        rewards_text = "\n" + rewards_text

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
