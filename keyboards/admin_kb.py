from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.study_kb import MATERIAL_TYPES


def admin_panel_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 ᴧᴅᴅ sᴛᴜᴅʏ ϻᴧᴛєʀiᴧʟ", callback_data="adm:add:study")],
        [InlineKeyboardButton(text="📝 ᴧᴅᴅ ǫᴜiᴢ ǫᴜєsᴛiση", callback_data="adm:add:quiz")],
        [InlineKeyboardButton(text="📊 sᴛᴧᴛs", callback_data="adm:stats")],
        [InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="menu:main")],
    ])


def adm_boards_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏫 ᴄʙsє", callback_data="adm:board:cbse"),
         InlineKeyboardButton(text="🏫 iᴄsє", callback_data="adm:board:icse")],
        [InlineKeyboardButton(text="⚡ ᴊєє", callback_data="adm:board:jee"),
         InlineKeyboardButton(text="🩺 ηєєᴛ", callback_data="adm:board:neet")],
        [InlineKeyboardButton(text="❌ ᴄᴧηᴄєʟ", callback_data="adm:cancel")],
    ])


def adm_classes_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="9️⃣ ᴄʟᴧss 9", callback_data="adm:cls:9"),
         InlineKeyboardButton(text="🔟 ᴄʟᴧss 10", callback_data="adm:cls:10")],
        [InlineKeyboardButton(text="1️⃣1️⃣ ᴄʟᴧss 11", callback_data="adm:cls:11"),
         InlineKeyboardButton(text="1️⃣2️⃣ ᴄʟᴧss 12", callback_data="adm:cls:12")],
        [InlineKeyboardButton(text="❌ ᴄᴧηᴄєʟ", callback_data="adm:cancel")],
    ])


def adm_subjects_kb(subjects):
    rows, row = [], []
    for s in subjects:
        row.append(InlineKeyboardButton(text=s, callback_data=f"adm:sub:{s}"))
        if len(row) == 2:
            rows.append(row); row = []
    if row: rows.append(row)
    rows.append([InlineKeyboardButton(text="❌ ᴄᴧηᴄєʟ", callback_data="adm:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def adm_material_type_kb():
    rows, row = [], []
    for label, code in MATERIAL_TYPES:
        row.append(InlineKeyboardButton(text=label, callback_data=f"adm:mt:{code}"))
        if len(row) == 2:
            rows.append(row); row = []
    if row: rows.append(row)
    rows.append([InlineKeyboardButton(text="❌ ᴄᴧηᴄєʟ", callback_data="adm:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def adm_confirm_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💾 sᴧᴠє", callback_data="adm:save"),
         InlineKeyboardButton(text="➕ ᴧᴅᴅ ϻσʀє", callback_data="adm:addmore")],
        [InlineKeyboardButton(text="❌ ᴄᴧηᴄєʟ", callback_data="adm:cancel")],
    ])


def adm_quiz_exam_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏫 ᴄʙsє", callback_data="qz:exam:cbse"),
         InlineKeyboardButton(text="🏫 iᴄsє", callback_data="qz:exam:icse")],
        [InlineKeyboardButton(text="⚡ ᴊєє ϻᴧiη", callback_data="qz:exam:jee_main"),
         InlineKeyboardButton(text="⚡ ᴊєє ᴧᴅᴠ", callback_data="qz:exam:jee_adv")],
        [InlineKeyboardButton(text="🩺 ηєєᴛ", callback_data="qz:exam:neet")],
        [InlineKeyboardButton(text="❌ ᴄᴧηᴄєʟ", callback_data="adm:cancel")],
    ])


def adm_quiz_confirm_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💾 sᴧᴠє ǫᴜєsᴛiση", callback_data="adm:qsave")],
        [InlineKeyboardButton(text="❌ ᴄᴧηᴄєʟ", callback_data="adm:cancel")],
    ])
