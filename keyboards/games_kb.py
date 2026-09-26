from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def games_main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎰 ғσʀᴛᴜηє", callback_data="game:fortune"),
         InlineKeyboardButton(text="⚔️ ᴧʀєηᴧ", callback_data="game:arena")],
        [InlineKeyboardButton(text="🐉 вєᴧsᴛ", callback_data="game:beast"),
         InlineKeyboardButton(text="🧩 ᴅєᴛєᴄᴛiᴠє", callback_data="game:detective")],
        [InlineKeyboardButton(text="🏹 ʀᴧiᴅ", callback_data="game:raid")],
        [InlineKeyboardButton(text="🏆 ɢᴧϻє ʟєᴧᴅєʀвσᴧʀᴅ", callback_data="game:lb_menu")],
        [InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="menu:main")],
    ])


def fortune_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎲 ʀσʟʟ (10 ᴄσiηs)", callback_data="fortune:bet:10"),
         InlineKeyboardButton(text="🎲 ʀσʟʟ (50 ᴄσiηs)", callback_data="fortune:bet:50")],
        [InlineKeyboardButton(text="💰 ʙiɢ ʀσʟʟ (100 ᴄσiηs)", callback_data="fortune:bet:100")],
        [InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="menu:games")],
    ])


def arena_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚔️ ᴧᴛᴛᴧᴄᴋ", callback_data="arena:attack"),
         InlineKeyboardButton(text="🛡️ ᴅєғєηᴅ", callback_data="arena:defend")],
        [InlineKeyboardButton(text="🏃 ғʟєє", callback_data="menu:games")],
    ])


def beast_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍖 ғєєᴅ (10 ᴄσiηs)", callback_data="beast:feed"),
         InlineKeyboardButton(text="🏋️ ᴛʀᴧiη", callback_data="beast:train")],
        [InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="menu:games")],
    ])


def detective_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 iηνєsᴛiɢᴧᴛє", callback_data="detective:investigate")],
        [InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="menu:games")],
    ])


def raid_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚔️ ᴧᴛᴛᴧᴄᴋ вσss", callback_data="raid:attack")],
        [InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="menu:games")],
    ])


def game_lb_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎰 ғσʀᴛᴜηє", callback_data="lb:fortune"),
         InlineKeyboardButton(text="⚔️ ᴧʀєηᴧ", callback_data="lb:arena")],
        [InlineKeyboardButton(text="🐉 вєᴧsᴛ", callback_data="lb:beast"),
         InlineKeyboardButton(text="🧩 ᴅєᴛєᴄᴛiᴠє", callback_data="lb:detective")],
        [InlineKeyboardButton(text="🏹 ʀᴧiᴅ", callback_data="lb:raid")],
        [InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="menu:games")],
    ])
