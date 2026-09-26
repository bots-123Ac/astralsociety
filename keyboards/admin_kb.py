from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def admin_panel_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📖 ᴧᴅᴅ ησᴛєs", callback_data="adm:add:notes"),
         InlineKeyboardButton(text="📝 ᴧᴅᴅ ᴅᴩᴩ", callback_data="adm:add:dpp")],
        [InlineKeyboardButton(text="📚 ᴧᴅᴅ ϻσᴅᴜʟє", callback_data="adm:add:modules"),
         InlineKeyboardButton(text="📕 ᴧᴅᴅ вσσᴋ", callback_data="adm:add:books")],
        [InlineKeyboardButton(text="❓ ᴧᴅᴅ ǫᴜєsᴛiσηs", callback_data="adm:add:questions"),
         InlineKeyboardButton(text="🗑️ ᴅєʟєᴛє ϻᴧᴛєʀiᴧʟ", callback_data="adm:delete")],
        [InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="menu:main")],
    ])


def admin_edu_kb(category: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏫 ᴄʙsє", callback_data=f"admedu:{category}:cbse"),
         InlineKeyboardButton(text="🏫 iᴄsє", callback_data=f"admedu:{category}:icse")],
        [InlineKeyboardButton(text="⚡ ᴊєє", callback_data=f"admedu:{category}:jee"),
         InlineKeyboardButton(text="🩺 ηєєᴛ", callback_data=f"admedu:{category}:neet")],
        [InlineKeyboardButton(text="❌ ᴄᴧηᴄєʟ", callback_data="admin:cancel")],
    ])


def admin_class_kb(category: str, edu: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="9️⃣ ᴄʟᴧss 9", callback_data=f"admcls:{category}:{edu}:9"),
         InlineKeyboardButton(text="🔟 ᴄʟᴧss 10", callback_data=f"admcls:{category}:{edu}:10")],
        [InlineKeyboardButton(text="1️⃣1️⃣ ᴄʟᴧss 11", callback_data=f"admcls:{category}:{edu}:11"),
         InlineKeyboardButton(text="1️⃣2️⃣ ᴄʟᴧss 12", callback_data=f"admcls:{category}:{edu}:12")],
        [InlineKeyboardButton(text="❌ ᴄᴧηᴄєʟ", callback_data="admin:cancel")],
    ])


def admin_subject_kb(category: str, edu: str, cls: str, subjects: list):
    rows = []
    row = []
    for s in subjects:
        row.append(InlineKeyboardButton(text=s, callback_data=f"admsub:{category}:{edu}:{cls}:{s}"))
        if len(row) == 2:
            rows.append(row); row = []
    if row: rows.append(row)
    rows.append([InlineKeyboardButton(text="❌ ᴄᴧηᴄєʟ", callback_data="admin:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
