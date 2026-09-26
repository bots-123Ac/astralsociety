from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from config import BOT_NAME

router = Router()


def study_menu_kb() -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(text="📖 ησᴛєs", callback_data="study:notes"),
            InlineKeyboardButton(text="📝 ᴅᴩᴩ", callback_data="study:dpp"),
        ],
        [
            InlineKeyboardButton(text="📚 ϻσᴅᴜʟєs", callback_data="study:modules"),
            InlineKeyboardButton(text="📕 вσσᴋs", callback_data="study:books"),
        ],
        [
            InlineKeyboardButton(text="❓ ᴩʀᴧᴄᴛiᴄє", callback_data="study:practice"),
            InlineKeyboardButton(text="🧠 ǫᴜiᴢᴢєs", callback_data="study:quiz"),
        ],
        [
            InlineKeyboardButton(text="🔍 sєᴧʀᴄн", callback_data="study:search"),
        ],
        [
            InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="menu:main"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


@router.callback_query(F.data == "menu:study")
async def show_study(callback: CallbackQuery):
    text = (
        f"📚 {BOT_NAME} — sᴛᴜᴅʏ\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ᴡнᴧᴛ ᴅσ ʏσᴜ ᴡᴧηηᴧ sᴛᴜᴅʏ тσᴅᴧʏ?"
    )
    await callback.message.edit_text(text, reply_markup=study_menu_kb())
    await callback.answer()


# ─── Category placeholders (baad me class/board/subject flow add hoga) ───

@router.callback_query(F.data.startswith("study:"))
async def study_category(callback: CallbackQuery):
    category = callback.data.split(":", 1)[1]
    category_names = {
        "notes": "📖 ησᴛєs",
        "dpp": "📝 ᴅᴩᴩ",
        "modules": "📚 ϻσᴅᴜʟєs",
        "books": "📕 вσσᴋs",
        "practice": "❓ ᴩʀᴧᴄᴛiᴄє ǫᴜєsᴛiσηs",
        "quiz": "🧠 ǫᴜiᴢᴢєs",
        "search": "🔍 sєᴧʀᴄн",
    }
    label = category_names.get(category, category)

    text = (
        f"{label}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🚧 тнis sєᴄᴛiση is ᴄσϻiηɢ sσση.\n"
        f"ᴀᴅᴍiηs ᴡiʟʟ вє ᴧвʟє тσ ᴜᴩʟσᴧᴅ ϻᴧᴛєʀiᴧʟ нєʀє."
    )
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="menu:study")]
        ]
    )
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()
