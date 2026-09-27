from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def games_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔤 ᴡᴏʀᴅ ɢᴜᴇssɪɴɢ", callback_data="wg:menu")],
        [InlineKeyboardButton(text="↩️ вᴀᴄᴋ", callback_data="menu:main")],
    ])


def word_length_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="4️⃣ 4 ʟᴇᴛᴛᴇʀs", callback_data="wg:new:4"),
         InlineKeyboardButton(text="5️⃣ 5 ʟᴇᴛᴛᴇʀs", callback_data="wg:new:5")],
        [InlineKeyboardButton(text="6️⃣ 6 ʟᴇᴛᴛᴇʀs", callback_data="wg:new:6")],
        [InlineKeyboardButton(text="↩️ вᴀᴄᴋ", callback_data="menu:games")],
    ])


def word_game_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 sᴛᴀᴛᴜs", callback_data="wg:status"),
         InlineKeyboardButton(text="🛑 ɢɪᴠᴇ ᴜᴘ", callback_data="wg:giveup")],
    ])


def leaderboard_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔤 ᴡᴏʀᴅ ɢᴀᴍᴇ", callback_data="lb:word")],
        [InlineKeyboardButton(text="📝 ǫᴜɪᴢ", callback_data="lb:quiz")],
        [InlineKeyboardButton(text="↩️ вᴀᴄᴋ", callback_data="menu:main")],
    ])
