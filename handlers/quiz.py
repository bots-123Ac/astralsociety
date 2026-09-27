from aiogram import Router, F
from aiogram.types import Message

from keyboards.main_menu import quiz_menu_kb

router = Router()


@router.message(F.text.regexp(r"^/quiz(\s|$)"))
async def cmd_quiz(message: Message):
    await message.answer(
        "🧠 <b>ᴀsᴛʀᴀʟ ǫᴜɪᴢ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "ᴄʜᴏᴏsᴇ ᴄᴀᴛᴇɢᴏʀʏ:",
        reply_markup=quiz_menu_kb()
    )
