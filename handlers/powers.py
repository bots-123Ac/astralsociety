from aiogram import Router, F
from aiogram.types import Message

from utils.database import get_active_powers
from utils.styler import fancy

router = Router()

POWER_NAMES = {
    "xp_boost": "⚡ xᴩ вσσsт",
}


@router.message(F.text.regexp(r"^/powers(\s|$)"))
async def cmd_powers(message: Message):
    powers = await get_active_powers(message.from_user.id)
    if not powers:
        return await message.reply("❌ ησ ᴩσωєʀs ᴧʀє ᴧᴩᴩʟiєᴅ ση ʏσᴜ.")

    lines = ["⚡ <b>ʏσᴜʀ ᴧᴄтiᴠє ᴩσωєʀs</b>", "━━━━━━━━━━━━━━━━━━━━━", ""]
    from datetime import datetime
    for power_type, expires_at in powers:
        label = POWER_NAMES.get(power_type, power_type)
        try:
            dt = datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
            days = max(0, (dt - datetime.utcnow()).days)
        except Exception:
            days = 0
        lines.append(f"{label} — {days} ᴅᴧʏs ʟєғт")
    await message.reply("\n".join(lines))
