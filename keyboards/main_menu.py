from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import SUPPORT_CHANNEL_LINK, SUPPORT_GROUP_LINK


def main_menu_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="📚 sᴛᴜᴅʏ", callback_data="menu:study")
    kb.button(text="🎮 ɢᴧϻєs", callback_data="menu:games")
    kb.button(text="🆘 нєʟᴩ", callback_data="menu:help")
    kb.button(text="ℹ️ ᴧвσᴜᴛ", callback_data="menu:about")
    kb.button(text="📢 sᴜᴩᴩσʀᴛ ᴄнᴧηηєʟ", url=SUPPORT_CHANNEL_LINK)
    kb.button(text="👥 sᴜᴩᴩσʀᴛ ɢʀσᴜᴩ", url=SUPPORT_GROUP_LINK)
    kb.button(text="👑 σᴡηєʀ", callback_data="menu:owner")
    kb.button(text="🥷 ᴋiᴅηᴧᴩ ϻє", callback_data="menu:kidnap")
    kb.adjust(2, 2, 1, 1, 2)
    return kb.as_markup()


def back_kb(target: str = "menu:main") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data=target)]
        ]
    )
