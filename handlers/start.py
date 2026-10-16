"""
handlers/start.py — /start + welcome message.
Uses shared welcome text so back button shows the same thing.
NO credits here — credits live only in /about.
"""

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, LinkPreviewOptions

from keyboards.main_menu import main_menu_kb
from utils.database import get_or_create_user
from utils.welcome import build_welcome_text

router = Router()


@router.message(CommandStart())
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
