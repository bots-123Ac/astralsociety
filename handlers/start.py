import logging
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import BOT_NAME, CREDIT_HTML
from keyboards.main_menu import main_menu_kb
from utils.database import get_or_create_user, register_group

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


@router.message(CommandStart())
async def cmd_start(message: Message):
    try:
        user = message.from_user
        await get_or_create_user(user.id, user.username, user.first_name)
        if message.chat.type in ("group", "supergroup"):
            try:
                await register_group(message.chat.id, message.chat.title or "")
            except Exception:
                pass

        text = welcome_text(user.first_name)
        kb = main_menu_kb()

        try:
            photos = await message.bot.get_user_profile_photos(user.id, limit=1)
            if photos.total_count > 0:
                file_id = photos.photos[0][-1].file_id
                await message.answer_photo(photo=file_id, caption=text, reply_markup=kb)
                return
        except Exception:
            pass

        await message.answer(text, reply_markup=kb)
    except Exception as e:
        logger.error(f"/start err: {e}")
        try:
            await message.answer("👋 ʜɪ! ᴘʟᴇᴀꜱᴇ ᴛʀʏ /start ᴀɢᴀɪɴ.")
        except Exception:
            pass
