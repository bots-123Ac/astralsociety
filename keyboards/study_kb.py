from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def study_main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📖 ησᴛєs", callback_data="study:cat:notes"),
         InlineKeyboardButton(text="📝 ᴅᴩᴩ", callback_data="study:cat:dpp")],
        [InlineKeyboardButton(text="📚 ϻσᴅᴜʟєs", callback_data="study:cat:modules"),
         InlineKeyboardButton(text="📕 вσσᴋs", callback_data="study:cat:books")],
        [InlineKeyboardButton(text="❓ ᴩʀᴧᴄᴛiᴄє", callback_data="study:cat:questions"),
         InlineKeyboardButton(text="🧠 ǫᴜiᴢᴢєs", callback_data="study:cat:quiz")],
        [InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="menu:main")],
    ])


def education_type_kb(category: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏫 ᴄʙsє", callback_data=f"edu:{category}:cbse"),
         InlineKeyboardButton(text="🏫 iᴄsє", callback_data=f"edu:{category}:icse")],
        [InlineKeyboardButton(text="⚡ ᴊєє", callback_data=f"edu:{category}:jee"),
         InlineKeyboardButton(text="🩺 ηєєᴛ", callback_data=f"edu:{category}:neet")],
        [InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="menu:study")],
    ])


def class_kb(category: str, edu: str):
    if edu in ("jee", "neet"):
        # JEE/NEET me class skip — seedha subject
        return None
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="9️⃣ ᴄʟᴧss 9", callback_data=f"cls:{category}:{edu}:9"),
         InlineKeyboardButton(text="🔟 ᴄʟᴧss 10", callback_data=f"cls:{category}:{edu}:10")],
        [InlineKeyboardButton(text="1️⃣1️⃣ ᴄʟᴧss 11", callback_data=f"cls:{category}:{edu}:11"),
         InlineKeyboardButton(text="1️⃣2️⃣ ᴄʟᴧss 12", callback_data=f"cls:{category}:{edu}:12")],
        [InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data=f"study:cat:{category}")],
    ])


SUBJECTS = {
    ("cbse", "9"): ["Maths", "Science", "English", "Social Science", "Hindi"],
    ("cbse", "10"): ["Maths", "Science", "English", "Social Science", "Hindi"],
    ("cbse", "11"): ["Physics", "Chemistry", "Maths", "Biology", "English"],
    ("cbse", "12"): ["Physics", "Chemistry", "Maths", "Biology", "English"],
    ("icse", "9"): ["Maths", "Physics", "Chemistry", "Biology", "English"],
    ("icse", "10"): ["Maths", "Physics", "Chemistry", "Biology", "English"],
    ("icse", "11"): ["Physics", "Chemistry", "Maths", "Biology", "English"],
    ("icse", "12"): ["Physics", "Chemistry", "Maths", "Biology", "English"],
    ("jee", "na"): ["Physics", "Chemistry", "Maths"],
    ("neet", "na"): ["Physics", "Chemistry", "Biology"],
}

CHAPTERS = {
    "Physics": ["Kinematics", "Laws of Motion", "Work & Energy", "Thermodynamics", "Optics"],
    "Chemistry": ["Atomic Structure", "Chemical Bonding", "Organic Basics", "Periodic Table"],
    "Maths": ["Algebra", "Trigonometry", "Calculus", "Coordinate Geometry", "Probability"],
    "Biology": ["Cell Biology", "Genetics", "Human Physiology", "Ecology", "Evolution"],
    "Science": ["Physics Basics", "Chemistry Basics", "Biology Basics"],
    "English": ["Grammar", "Literature", "Writing Skills"],
    "Social Science": ["History", "Geography", "Civics", "Economics"],
    "Hindi": ["Vyakaran", "Sahitya"],
}


def subject_kb(category: str, edu: str, cls: str):
    key = (edu, cls)
    subjects = SUBJECTS.get(key, [])
    rows = []
    row = []
    for i, s in enumerate(subjects):
        row.append(InlineKeyboardButton(text=s, callback_data=f"sub:{category}:{edu}:{cls}:{s}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data=f"study:cat:{category}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def chapter_kb(category: str, edu: str, cls: str, subject: str):
    chapters = CHAPTERS.get(subject, [])
    rows = []
    for ch in chapters:
        rows.append([InlineKeyboardButton(text=ch, callback_data=f"chp:{category}:{edu}:{cls}:{subject}:{ch}")])
    rows.append([InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data=f"cls:{category}:{edu}:{cls}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
