from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from config import BOT_NAME

router = Router()


def games_menu_kb() -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(text="🎰 ғσʀᴛᴜηє", callback_data="game:fortune"),
            InlineKeyboardButton(text="⚔️ ᴧʀєηᴧ", callback_data="game:arena"),
        ],
        [
            InlineKeyboardButton(text="🐉 вєᴧsᴛ", callback_data="game:beast"),
            InlineKeyboardButton(text="🧩 ᴅєᴛєᴄᴛiᴠє", callback_data="game:detective"),
        ],
        [
            InlineKeyboardButton(text="🏹 ʀᴧiᴅ", callback_data="game:raid"),
        ],
        [
            InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="menu:main"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


@router.callback_query(F.data == "menu:games")
async def show_games(callback: CallbackQuery):
    text = (
        f"🎮 {BOT_NAME} — ɢᴧϻєs\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ᴄнσσsє ᴧ ɢᴧϻє тσ ᴩʟᴧʏ:\n\n"
        f"єᴧᴄн ɢᴧϻє нᴧs its σᴡη єᴄσησϻʏ, "
        f"ᴜᴩɢʀᴧᴅєs & ʟєᴧᴅєʀвσᴧʀᴅ."
    )
    await callback.message.edit_text(text, reply_markup=games_menu_kb())
    await callback.answer()


@router.callback_query(F.data.startswith("game:"))
async def game_selected(callback: CallbackQuery):
    game = callback.data.split(":", 1)[1]
    game_names = {
        "fortune": "🎰 ᴧsᴛʀᴧʟ ғσʀᴛᴜηє",
        "arena": "⚔️ ᴧsᴛʀᴧʟ ᴧʀєηᴧ",
        "beast": "🐉 ᴧsᴛʀᴧʟ вєᴧsᴛ",
        "detective": "🧩 ᴧsᴛʀᴧʟ ᴅєᴛєᴄᴛiᴠє",
        "raid": "🏹 ᴧsᴛʀᴧʟ ʀᴧiᴅ",
    }
    label = game_names.get(game, game)

    text = (
        f"{label}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🚧 тнis ɢᴧϻє is ᴄσϻiηɢ sσση.\n"
        f"sᴛᴧʏ тᴜηєᴅ ғσʀ ᴜᴩᴅᴧᴛєs!"
    )
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="menu:games")]
        ]
    )
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()
