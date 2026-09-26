from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import BOT_NAME
from keyboards.main_menu import main_menu_kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    text = (
        f"👋 нi {message.from_user.first_name}!\n\n"
        f"i'ϻ {BOT_NAME} — ʏσᴜʀ ᴧʟʟ-iη-σηє тєʟєɢʀᴧϻ "
        f"ᴄσϻᴩᴧηiση ғσʀ sᴛᴜᴅʏ, ɢʀσᴜᴩs, ɢᴧϻєs & ϻσʀє.\n\n"
        f"ᴄнσσsє ᴧη σᴩᴛiση вєʟσᴡ 👇"
    )
    await message.answer(text, reply_markup=main_menu_kb())
