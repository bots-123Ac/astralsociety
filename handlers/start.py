"""
handlers/start.py — /start + welcome message + group auto-tracking.

• /start: DM only (no welcome spam in groups)
• Auto-registers every group where the bot sees activity
"""

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, LinkPreviewOptions

from keyboards.main_menu import main_menu_kb
from utils.database import (
    get_or_create_user, auto_register_group_from_message,
)
from utils.welcome import build_welcome_text

router = Router()


# ═══════════════════════════════════════════════
# /start — DM ONLY
# ═══════════════════════════════════════════════
@router.message(CommandStart(), F.chat.type == "private")
async def cmd_start(message: Message):
    await get_or_create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
    )

    await message.answer(
        build_welcome_text(message.from_user.first_name or "User"),
        reply_markup=main_menu_kb(),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )


# ═══════════════════════════════════════════════
# AUTO-REGISTER GROUPS ON ANY MESSAGE
# ═══════════════════════════════════════════════
@router.message(F.chat.type.in_({"group", "supergroup"}))
async def auto_track_group(message: Message):
    """Silently registers any group where the bot sees activity."""
    try:
        await auto_register_group_from_message(
            message.chat.id,
            message.chat.title or "",
        )
    except Exception:
        pass
    # Don't reply — just track silently
