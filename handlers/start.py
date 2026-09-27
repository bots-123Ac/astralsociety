import logging
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import BOT_NAME
from keyboards.main_menu import main_menu_kb
from utils.database import get_or_create_user

router = Router()
logger = logging.getLogger(__name__)


def welcome_text(first_name: str) -> str:
    return (
        f"👋 нi, <b>{first_name}</b>!\n\n"
        f"ᴡєʟᴄσϻє тσ <b>{BOT_NAME}</b> 🌌\n\n"
        f"🎓 sᴛᴜᴅʏ  •  📝 ǫᴜiᴢ  •  🎮 ɢᴧϻєs\n"
        f"🏆 ʟєᴧᴅєʀвσᴧʀᴅ  •  👤 ᴩʀσғiʟє\n\n"
        f"ᴄнσσsє ᴧη σᴩᴛiση вєʟσᴡ 👇"
    )


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Always respond — robust error handling."""
    try:
        user = message.from_user
        try:
            await get_or_create_user(user.id, user.username, user.first_name)
        except Exception as e:
            logger.warning(f"DB register failed: {e}")

        text = welcome_text(user.first_name)
        kb = main_menu_kb()

        # Try sending with PFP
        try:
            photos = await message.bot.get_user_profile_photos(user.id, limit=1)
            if photos.total_count > 0:
                file_id = photos.photos[0][-1].file_id
                await message.answer_photo(photo=file_id, caption=text, reply_markup=kb)
                return
        except Exception as e:
            logger.warning(f"PFP fetch failed: {e}")

        await message.answer(text, reply_markup=kb)
    except Exception as e:
        logger.error(f"/start error: {e}")
        try:
            await message.answer("👋 нi! ᴩʟєᴧsє тʀʏ /start ᴧɢᴧiη.")
        except Exception:
            pass
