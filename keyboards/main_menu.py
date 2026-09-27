from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import SUPPORT_GROUP_LINK, SUPPORT_CHANNEL_LINK, BOT_ADD_LINK


def main_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆘 нєʟᴩ", callback_data="menu:help"),
         InlineKeyboardButton(text="ℹ️ ᴧвσᴜᴛ", callback_data="menu:about")],
        [InlineKeyboardButton(text="👥 sᴜᴩᴩσʀᴛiᴠє ɢᴄ", url=SUPPORT_GROUP_LINK)],
        [InlineKeyboardButton(text="📢 sᴜᴩᴩσʀᴛiᴠє ᴄнᴧηηєʟ", url=SUPPORT_CHANNEL_LINK)],
        [InlineKeyboardButton(text="🥷 ᴋiᴅηᴧᴩ ϻє", url=BOT_ADD_LINK)],
    ])


def back_kb(target="menu:main"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data=target)]
    ])


def back_main_kb():
    return back_kb("menu:main")


# ═══ Game keyboards (used in /tgames) ═══
def tgames_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧠 ǫᴜiᴢ", callback_data="tg:quiz")],
        [InlineKeyboardButton(text="🔤 ᴡσʀᴅ ɢᴜєssiηɢ", callback_data="tg:word")],
        [InlineKeyboardButton(text="🔢 ɢᴜєss тнє ηᴜϻвєʀ", callback_data="tg:number")],
    ])


def quiz_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 sᴩᴧᴄє ǫᴜiᴢ", callback_data="quiz:space")],
        [InlineKeyboardButton(text="🌍 ɢєηєʀᴧʟ ǫᴜiᴢ", callback_data="quiz:general")],
    ])


def quiz_options_kb(qid, a, b, c, d):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"ᴀ) {a[:40]}", callback_data=f"qans:{qid}:A")],
        [InlineKeyboardButton(text=f"ʙ) {b[:40]}", callback_data=f"qans:{qid}:B")],
        [InlineKeyboardButton(text=f"ᴄ) {c[:40]}", callback_data=f"qans:{qid}:C")],
        [InlineKeyboardButton(text=f"ᴅ) {d[:40]}", callback_data=f"qans:{qid}:D")],
    ])


# ═══ Leaderboard ═══
def leaderboard_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 ɢʀσᴜᴩ тσᴩ 10", callback_data="lb:group")],
        [InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="menu:main")],
    ])


# ═══ Study ═══
def study_class_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📘 ᴄʟᴧss 10", callback_data="study:10"),
         InlineKeyboardButton(text="📗 ᴄʟᴧss 11", callback_data="study:11")],
        [InlineKeyboardButton(text="📕 ᴄʟᴧss 12", callback_data="study:12")],
        [InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="menu:main")],
    ])


def study_class10_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔬 sᴄiєηᴄє", callback_data="st10:subject:science"),
         InlineKeyboardButton(text="📐 ϻᴧтнs", callback_data="st10:subject:maths")],
        [InlineKeyboardButton(text="🌍 ssт", callback_data="st10:subject:sst"),
         InlineKeyboardButton(text="📖 єηɢʟisн", callback_data="st10:subject:english")],
        [InlineKeyboardButton(text="📝 ᴩʏǫ", callback_data="st10:section:pyq")],
        [InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="menu:study")],
    ])


def study_class1112_kb(class_name):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 ᴊєє", callback_data=f"st{class_name}:section:jee")],
        [InlineKeyboardButton(text="🩺 ηєєᴛ", callback_data=f"st{class_name}:section:neet")],
        [InlineKeyboardButton(text="🎯🩺 ᴊєє + ηєєᴛ", callback_data=f"st{class_name}:section:both")],
        [InlineKeyboardButton(text="📝 ᴩʏǫs", callback_data=f"st{class_name}:section:pyq")],
        [InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="menu:study")],
    ])


def chapters_kb(class_name, section, chapters, subject=None):
    rows = []
    for i, ch in enumerate(chapters):
        cb = f"stch:{class_name}:{section}:{i}"
        if subject:
            cb = f"stch:{class_name}:{section}:{i}:{subject}"
        rows.append([InlineKeyboardButton(text=f"📄 {ch}", callback_data=cb)])
    rows.append([InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="menu:study")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ═══ Shop ═══
def shop_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👁️ ᴩʀσтєᴄтiση ᴄнєᴄᴋєʀ (6💎)", callback_data="shop:checker")],
        [InlineKeyboardButton(text="⚡ xᴩ вσσsт", callback_data="shop:xpboost")],
        [InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="menu:main")],
    ])


def xpboost_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="5 ᴅᴧʏs — 6💎", callback_data="shop:xp:5")],
        [InlineKeyboardButton(text="7 ᴅᴧʏs — 8💎", callback_data="shop:xp:7")],
        [InlineKeyboardButton(text="12 ᴅᴧʏs — 13💎", callback_data="shop:xp:12")],
        [InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="shop:back")],
    ])


# ═══ Premium ═══
def premium_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 ϻσηтн — 90⭐", callback_data="prem:1m")],
        [InlineKeyboardButton(text="4 ϻσηтнs — 140⭐", callback_data="prem:4m")],
        [InlineKeyboardButton(text="12 ϻσηтнs — 175⭐", callback_data="prem:12m")],
        [InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="menu:main")],
    ])
