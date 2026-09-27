from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def quiz_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏫 ᴄʙsє", callback_data="qz:start:cbse"),
         InlineKeyboardButton(text="🏫 iᴄsє", callback_data="qz:start:icse")],
        [InlineKeyboardButton(text="⚡ ᴊєє ϻᴧiη", callback_data="qz:start:jee_main"),
         InlineKeyboardButton(text="⚡ ᴊєє ᴧᴅᴠ", callback_data="qz:start:jee_adv")],
        [InlineKeyboardButton(text="🩺 ηєєᴛ", callback_data="qz:start:neet")],
        [InlineKeyboardButton(text="🎲 ʀᴧηᴅσϻ", callback_data="qz:start:any")],
        [InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="menu:main")],
    ])


def quiz_question_kb(qid, options):
    """options = [('A', 'text'), ('B', 'text'), ...]"""
    rows = []
    for key, text in options:
        # Truncate long option text
        short = text if len(text) <= 40 else text[:37] + "..."
        rows.append([InlineKeyboardButton(
            text=f"{key}) {short}",
            callback_data=f"qz:ans:{qid}:{key}"
        )])
    rows.append([InlineKeyboardButton(text="⏭️ sᴋiᴩ", callback_data="qz:skip"),
                 InlineKeyboardButton(text="⏹️ єηᴅ", callback_data="qz:end")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def quiz_after_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➡️ ηєxᴛ ǫᴜєsᴛiση", callback_data="qz:next")],
        [InlineKeyboardButton(text="⏹️ єηᴅ ǫᴜiᴢ", callback_data="qz:end")],
    ])
