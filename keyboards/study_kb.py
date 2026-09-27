from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

MATERIAL_TYPES = [
    ("📖 ησᴛєs", "notes"),
    ("📕 вσσᴋs", "books"),
    ("📝 ᴅᴩᴩ", "dpp"),
    ("📄 ᴩʏǫ", "pyq"),
    ("❓ ᴩʀᴧᴄᴛiᴄє", "practice"),
]

MATERIAL_LABELS = {k: v for v, k in MATERIAL_TYPES}

SUBJECTS_BY_BOARD = {
    "cbse_9": ["Science", "Maths", "English", "Social Science", "Hindi"],
    "cbse_10": ["Science", "Maths", "English", "Social Science", "Hindi"],
    "cbse_11": ["Physics", "Chemistry", "Biology", "Maths", "English"],
    "cbse_12": ["Physics", "Chemistry", "Biology", "Maths", "English"],
    "icse_9": ["Physics", "Chemistry", "Biology", "Maths", "English"],
    "icse_10": ["Physics", "Chemistry", "Biology", "Maths", "English"],
    "icse_11": ["Physics", "Chemistry", "Biology", "Maths", "English"],
    "icse_12": ["Physics", "Chemistry", "Biology", "Maths", "English"],
    "jee": ["Physics", "Chemistry", "Maths"],
    "neet": ["Physics", "Chemistry", "Biology"],
}


def boards_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏫 ᴄʙsє", callback_data="study:board:cbse"),
         InlineKeyboardButton(text="🏫 iᴄsє", callback_data="study:board:icse")],
        [InlineKeyboardButton(text="⚡ ᴊєє", callback_data="study:board:jee"),
         InlineKeyboardButton(text="🩺 ηєєᴛ", callback_data="study:board:neet")],
        [InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="menu:main")],
    ])


def classes_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="9️⃣ ᴄʟᴧss 9", callback_data="study:cls:9"),
         InlineKeyboardButton(text="🔟 ᴄʟᴧss 10", callback_data="study:cls:10")],
        [InlineKeyboardButton(text="1️⃣1️⃣ ᴄʟᴧss 11", callback_data="study:cls:11"),
         InlineKeyboardButton(text="1️⃣2️⃣ ᴄʟᴧss 12", callback_data="study:cls:12")],
        [InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="menu:study")],
    ])


def subjects_kb(board, cls, subjects):
    rows, row = [], []
    for s in subjects:
        row.append(InlineKeyboardButton(text=s, callback_data=f"study:sub:{s}"))
        if len(row) == 2:
            rows.append(row); row = []
    if row: rows.append(row)
    back = "menu:study" if board in ("jee", "neet") else "study:back:cls"
    rows.append([InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data=back)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def chapters_kb(chapters):
    rows = []
    for i, (ch, count) in enumerate(chapters):
        rows.append([InlineKeyboardButton(
            text=f"📄 {ch} ({count})",
            callback_data=f"study:chp:{i}"
        )])
    rows.append([InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="study:back:sub")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def materials_kb(materials):
    rows = []
    for mtype, count in materials:
        label = MATERIAL_LABELS.get(mtype, mtype)
        rows.append([InlineKeyboardButton(
            text=f"{label} ({count})",
            callback_data=f"study:mat:{mtype}"
        )])
    rows.append([InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="study:back:chp")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
