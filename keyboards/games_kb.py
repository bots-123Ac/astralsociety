from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def games_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔤 ᴡσʀᴅ ɢᴜєssiηɢ", callback_data="wg:menu")],
        [InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="menu:main")],
    ])


def word_length_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="4️⃣ 4 ʟєᴛᴛєʀs", callback_data="wg:new:4"),
         InlineKeyboardButton(text="5️⃣ 5 ʟєᴛᴛєʀs", callback_data="wg:new:5")],
        [InlineKeyboardButton(text="6️⃣ 6 ʟєᴛᴛєʀs", callback_data="wg:new:6")],
        [InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="menu:games")],
    ])


def word_game_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 sᴛᴧтᴜs", callback_data="wg:status"),
         InlineKeyboardButton(text="🛑 ɢivє ᴜᴩ", callback_data="wg:giveup")],
    ])


def leaderboard_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔤 ᴡσʀᴅ ɢᴧϻє", callback_data="lb:word")],
        [InlineKeyboardButton(text="📝 ǫᴜiᴢ", callback_data="lb:quiz")],
        [InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="menu:main")],
    ])
