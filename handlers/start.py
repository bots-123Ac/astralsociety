import logging
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import BOT_NAME, CREDIT_HTML
from keyboards.main_menu import main_menu_kb
from utils.database import get_or_create_user

router = Router()
logger = logging.getLogger(__name__)


def welcome_text(first_name: str) -> str:
    return (
        f"👋 ʜɪ, <b>{first_name}</b>!\n\n"
        f"ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ <b>{BOT_NAME}</b> 🌌\n\n"
        f"ʏᴏᴜʀ ᴀʟʟ-ɪɴ-ᴏɴᴇ ᴛᴇʟᴇɢʀᴀᴍ ᴄᴏᴍᴘᴀɴɪᴏɴ ғᴏʀ\n"
        f"ꜱᴛᴜᴅʏ, ɢᴀᴍᴇꜱ ᴀɴᴅ ᴍᴏʀᴇ.\n\n"
        f"ᴄʜᴏᴏꜱᴇ ᴀɴ ᴏᴘᴛɪᴏɴ ʙᴇʟᴏᴡ 👇\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"👨‍💻 {CREDIT_HTML}"
    )


async def send_welcome(message: Message):
    user = message.from_user
    try:
        await get_or_create_user(user.id, user.username, user.first_name)
    except Exception as e:
        logger.warning(f"register failed: {e}")

    text = welcome_text(user.first_name)
    kb = main_menu_kb()

    try:
        photos = await message.bot.get_user_profile_photos(user.id, limit=1)
        if photos.total_count > 0:
            file_id = photos.photos[0][-1].file_id
            await message.answer_photo(photo=file_id, caption=text, reply_markup=kb)
            return
    except Exception as e:
        logger.warning(f"pfp failed: {e}")

    await message.answer(text, reply_markup=kb)


@router.message(CommandStart())
async def cmd_start(message: Message):
    try:
        await send_welcome(message)
    except Exception as e:
        logger.error(f"/start err: {e}")
        try:
            await message.answer("👋 нi! ᴩʟєᴧsє тʀʏ /start ᴧɢᴧiη.")
        except Exception:
            pass
