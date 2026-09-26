from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

RESOURCE_TYPES = [
    ("📖 ησᴛєs", "notes"),
    ("📝 ᴅᴩᴩ", "dpp"),
    ("📚 ϻσᴅᴜʟєs", "modules"),
    ("📕 вσσᴋs", "books"),
    ("❓ ᴩʀᴧᴄᴛiᴄє", "questions"),
    ("🧠 ǫᴜiᴢᴢєs", "quiz"),
]

RESOURCE_TYPE_LABELS = {
    "notes": "📖 ησᴛєs", "dpp": "📝 ᴅᴩᴩ", "modules": "📚 ϻσᴅᴜʟєs",
    "books": "📕 вσσᴋs", "questions": "❓ ᴩʀᴧᴄᴛiᴄє", "quiz": "🧠 ǫᴜiᴢᴢєs",
    "video": "🎥 ᴠiᴅєσs", "pdf": "📁 ᴩᴅғ", "link": "🔗 ʟiηᴋs",
    "image": "🖼️ iϻᴧɢєs", "other": "➕ σᴛнєʀ",
}

CATEGORIES = [
    ("🔬 sᴄiєηᴄє", "science"),
    ("💼 ᴄσϻϻєʀᴄє", "commerce"),
    ("🎨 ᴧʀᴛs", "arts"),
    ("📚 ɢєηєʀᴧʟ", "general"),
]

SUBJECTS_BY_CATEGORY = {
    "science": ["Physics", "Chemistry", "Biology", "Maths"],
    "commerce": ["Accountancy", "Business Studies", "Economics"],
    "arts": ["History", "Geography", "Political Science"],
    "general": ["Science", "Maths", "English", "Social Science"],
}


def study_main_kb():
    rows, row = [], []
    for label, code in RESOURCE_TYPES:
        row.append(InlineKeyboardButton(text=label, callback_data=f"study:rt:{code}"))
        if len(row) == 2:
            rows.append(row); row = []
    if row: rows.append(row)
    rows.append([InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def education_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏫 ᴄʙsє", callback_data="study:edu:cbse"),
         InlineKeyboardButton(text="🏫 iᴄsє", callback_data="study:edu:icse")],
        [InlineKeyboardButton(text="⚡ ᴊєє", callback_data="study:edu:jee"),
         InlineKeyboardButton(text="🩺 ηєєᴛ", callback_data="study:edu:neet")],
        [InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="menu:study")],
    ])


def class_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="9️⃣ ᴄʟᴧss 9", callback_data="study:cls:9"),
         InlineKeyboardButton(text="🔟 ᴄʟᴧss 10", callback_data="study:cls:10")],
        [InlineKeyboardButton(text="1️⃣1️⃣ ᴄʟᴧss 11", callback_data="study:cls:11"),
         InlineKeyboardButton(text="1️⃣2️⃣ ᴄʟᴧss 12", callback_data="study:cls:12")],
        [InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="study:back:edu")],
    ])


def category_kb():
    rows = [[InlineKeyboardButton(text=l, callback_data=f"study:cat:{c}")] for l, c in CATEGORIES]
    rows.append([InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="study:back:cls")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def subject_kb(category):
    subjects = SUBJECTS_BY_CATEGORY.get(category, [])
    rows, row = [], []
    for s in subjects:
        row.append(InlineKeyboardButton(text=s, callback_data=f"study:sub:{s}"))
        if len(row) == 2:
            rows.append(row); row = []
    if row: rows.append(row)
    rows.append([InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="study:back:cat")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def chapters_kb(chapters):
    """chapters = [(chapter_name, count), ...]. Uses index in callback to avoid long data."""
    rows = []
    for i, (ch, count) in enumerate(chapters):
        rows.append([InlineKeyboardButton(
            text=f"📄 {ch} ({count})",
            callback_data=f"study:chp:{i}"
        )])
    rows.append([InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="study:back:sub")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
