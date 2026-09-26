from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import SUPPORT_GROUP_LINK, SUPPORT_CHANNEL_LINK


def main_menu_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="📚 sᴛᴜᴅʏ", callback_data="menu:study")
    kb.button(text="🎮 ɢᴧϻєs", callback_data="menu:games")
    kb.button(text="👤 ᴩʀσғiʟє", callback_data="menu:profile")
    kb.button(text="🏆 ʟєᴧᴅєʀвσᴧʀᴅ", callback_data="menu:leaderboard")
    kb.button(text="🆘 нєʟᴩ", callback_data="menu:help")
    kb.button(text="ℹ️ ᴧвσᴜᴛ", callback_data="menu:about")
    kb.button(text="📢 ᴄнᴧηηєʟ", url=SUPPORT_CHANNEL_LINK)
    kb.button(text="👑 σᴡηєʀ / sᴜᴩᴩσʀᴛ ɢᴄ", url=SUPPORT_GROUP_LINK)
    kb.button(text="🥷 ᴋiᴅηᴧᴩ ϻє", callback_data="menu:kidnap")
    kb.adjust(2, 2, 2, 1, 1, 1)
    return kb.as_markup()


def back_kb(target: str = "menu:main") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data=target)]
    ])


def cancel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ ᴄᴧηᴄєʟ", callback_data="admin:cancel")]
    ])
