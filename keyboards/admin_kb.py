from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.study_kb import CATEGORIES, SUBJECTS_BY_CATEGORY


def admin_panel_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 ᴧᴅᴅ ʀєsσᴜʀᴄє", callback_data="adm:add")],
        [InlineKeyboardButton(text="🗑️ ϻᴧηᴧɢє", callback_data="adm:manage")],
        [InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="menu:main")],
    ])


def admin_education_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏫 ᴄʙsє", callback_data="adm:edu:cbse"),
         InlineKeyboardButton(text="🏫 iᴄsє", callback_data="adm:edu:icse")],
        [InlineKeyboardButton(text="⚡ ᴊєє", callback_data="adm:edu:jee"),
         InlineKeyboardButton(text="🩺 ηєєᴛ", callback_data="adm:edu:neet")],
        [InlineKeyboardButton(text="❌ ᴄᴧηᴄєʟ", callback_data="adm:cancel")],
    ])


def admin_class_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="9️⃣ ᴄʟᴧss 9", callback_data="adm:cls:9"),
         InlineKeyboardButton(text="🔟 ᴄʟᴧss 10", callback_data="adm:cls:10")],
        [InlineKeyboardButton(text="1️⃣1️⃣ ᴄʟᴧss 11", callback_data="adm:cls:11"),
         InlineKeyboardButton(text="1️⃣2️⃣ ᴄʟᴧss 12", callback_data="adm:cls:12")],
        [InlineKeyboardButton(text="❌ ᴄᴧηᴄєʟ", callback_data="adm:cancel")],
    ])


def admin_category_kb():
    rows = [[InlineKeyboardButton(text=l, callback_data=f"adm:cat:{c}")] for l, c in CATEGORIES]
    rows.append([InlineKeyboardButton(text="❌ ᴄᴧηᴄєʟ", callback_data="adm:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def admin_subject_kb(category):
    subjects = SUBJECTS_BY_CATEGORY.get(category, [])
    rows, row = [], []
    for s in subjects:
        row.append(InlineKeyboardButton(text=s, callback_data=f"adm:sub:{s}"))
        if len(row) == 2:
            rows.append(row); row = []
    if row: rows.append(row)
    rows.append([InlineKeyboardButton(text="❌ ᴄᴧηᴄєʟ", callback_data="adm:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def admin_resource_type_kb():
    types = [
        ("📖 ησᴛєs", "notes"), ("❓ ǫᴜєsтiση вᴧηᴋ", "questions"),
        ("📄 ᴅᴩᴩ", "dpp"), ("📚 ϻσᴅᴜʟє", "modules"),
        ("🎥 ᴠiᴅєσ", "video"), ("📕 вσσᴋ", "books"),
        ("🔗 ʟiηᴋ", "link"), ("🖼️ iϻᴧɢє", "image"),
        ("📁 ᴩᴅғ", "pdf"), ("➕ σᴛнєʀ", "other"),
    ]
    rows, row = [], []
    for label, code in types:
        row.append(InlineKeyboardButton(text=label, callback_data=f"adm:rt:{code}"))
        if len(row) == 2:
            rows.append(row); row = []
    if row: rows.append(row)
    rows.append([InlineKeyboardButton(text="❌ ᴄᴧηᴄєʟ", callback_data="adm:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def admin_save_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💾 sᴧᴠє", callback_data="adm:save"),
         InlineKeyboardButton(text="➕ ᴧᴅᴅ ϻσʀє", callback_data="adm:addmore")],
        [InlineKeyboardButton(text="❌ ᴄᴧηᴄєʟ", callback_data="adm:cancel")],
    ])
