import logging
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile
from aiogram.exceptions import TelegramBadRequest

from config import BOT_NAME
from keyboards.main_menu import main_menu_kb
from utils.database import get_or_create_user

router = Router()
logger = logging.getLogger(__name__)


async def send_start(message: Message):
    user = message.from_user
    await get_or_create_user(user.id, user.username, user.first_name)

    text = (
        f"👋 нi, <b>{user.first_name}</b>!\n\n"
        f"ᴡєʟᴄσϻє тσ <b>{BOT_NAME}</b> 🌌\n\n"
        f"ʏσᴜʀ ᴧʟʟ-iη-σηє ᴛєʟєɢʀᴧϻ ᴄσϻᴩᴧηiση ғσʀ:\n\n"
        f"🎓 sᴛᴜᴅʏ\n"
        f"🛡️ ɢʀσᴜᴩ ϻᴧηᴧɢєϻєηᴛ\n"
        f"🎮 ɢᴧϻєs & єηᴛєʀᴛᴧiηϻєηᴛ\n\n"
        f"ᴄнσσsє ᴧη σᴩᴛiση вєʟσᴡ 👇"
    )

    # Try user's PFP first
    sent_photo = False
    try:
        photos = await message.bot.get_user_profile_photos(user.id, limit=1)
        if photos.total_count > 0:
            file_id = photos.photos[0][-1].file_id
            await message.answer_photo(photo=file_id, caption=text, reply_markup=main_menu_kb())
            sent_photo = True
    except TelegramBadRequest:
        pass
    except Exception as e:
        logger.warning(f"PFP fetch failed: {e}")

    if not sent_photo:
        await message.answer(text, reply_markup=main_menu_kb())


@router.message(CommandStart())
async def cmd_start(message: Message):
    await send_start(message)
