import logging
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import BOT_NAME
from keyboards.main_menu import main_menu_kb
from utils.database import get_or_create_user

router = Router()
logger = logging.getLogger(__name__)


def _welcome_text(first_name: str) -> str:
    return (
        f"👋 нi, <b>{first_name}</b>!\n\n"
        f"ᴡєʟᴄσϻє тσ <b>{BOT_NAME}</b> 🌌\n\n"
        f"ʏσᴜʀ ᴧʟʟ-iη-σηє ᴛєʟєɢʀᴧϻ ᴄσϻᴩᴧηiση ғσʀ:\n\n"
        f"🎓 sᴛᴜᴅʏ\n"
        f"🛡️ ɢʀσᴜᴩ ϻᴧηᴧɢєϻєηᴛ\n"
        f"🎮 ɢᴧϻєs & єηᴛєʀᴛᴧiηϻєηᴛ\n\n"
        f"ᴄнσσsє ᴧη σᴩᴛiση вєʟσᴡ 👇"
    )


async def send_start(message: Message):
    user = message.from_user
    try:
        await get_or_create_user(user.id, user.username, user.first_name)
    except Exception as e:
        logger.warning(f"DB error: {e}")

    text = _welcome_text(user.first_name)
    kb = main_menu_kb()

    # Try sending with user's PFP
    try:
        photos = await message.bot.get_user_profile_photos(user.id, limit=1)
        if photos.total_count > 0:
            file_id = photos.photos[0][-1].file_id
            await message.answer_photo(photo=file_id, caption=text, reply_markup=kb)
            return
    except Exception as e:
        logger.warning(f"PFP fetch failed: {e}")

    # Fallback: plain text
    try:
        await message.answer(text, reply_markup=kb)
    except Exception as e:
        logger.error(f"Start message failed: {e}")
        # Last resort: minimal message
        await message.answer("👋 нi! ᴜsє /start ᴧɢᴧiη ᴩʟєᴧsє.")


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Always respond to /start — never skip, never crash."""
    try:
        await send_start(message)
    except Exception as e:
        logger.error(f"/start handler error: {e}")
        try:
            await message.answer("👋 нi! ᴜsᴇ вᴜᴛᴛσηs тσ ηᴧᴠiɢᴧᴛє.")
        except Exception:
            pass
