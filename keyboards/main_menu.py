from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import SUPPORT_GROUP_LINK, SUPPORT_CHANNEL_LINK, BOT_ADD_LINK


def main_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆘 ʜᴇʟᴘ", callback_data="menu:help"),
         InlineKeyboardButton(text="ℹ️ ᴀʙᴏᴜᴛ", callback_data="menu:about")],
        [InlineKeyboardButton(text="👥 ꜱᴜᴘᴘᴏʀᴛɪᴠᴇ ɢᴄ", url=SUPPORT_GROUP_LINK)],
        [InlineKeyboardButton(text="📢 ꜱᴜᴘᴘᴏʀᴛɪᴠᴇ ᴄʜᴀɴɴᴇʟ", url=SUPPORT_CHANNEL_LINK)],
        [InlineKeyboardButton(text="🥷 ᴋɪᴅɴᴀᴘ ᴍᴇ", url=BOT_ADD_LINK)],
    ])


def back_kb(target="menu:main"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ ʙᴀᴄᴋ", callback_data=target)]
    ])


def back_main_kb():
    return back_kb("menu:main")


def tgames_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧠 ǫᴜɪᴢ", callback_data="tg:quiz")],
        [InlineKeyboardButton(text="🔢 ɢᴜᴇꜱꜱ ᴛʜᴇ ɴᴜᴍʙᴇʀ", callback_data="tg:number")],
    ])


def quiz_count_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="5 ǫᴜᴇꜱᴛɪᴏɴꜱ", callback_data="qzcount:5"),
         InlineKeyboardButton(text="10 ǫᴜᴇꜱᴛɪᴏɴꜱ", callback_data="qzcount:10")],
        [InlineKeyboardButton(text="15 ǫᴜᴇꜱᴛɪᴏɴꜱ", callback_data="qzcount:15"),
         InlineKeyboardButton(text="20 ǫᴜᴇꜱᴛɪᴏɴꜱ", callback_data="qzcount:20")],
        [InlineKeyboardButton(text="↩️ ʙᴀᴄᴋ", callback_data="menu:main")],
    ])


def quiz_menu_kb():
    """15 categories in 2-column layout."""
    categories = [
        ("🚀 ꜱᴘᴀᴄᴇ", "quiz:space"),
        ("🌍 ɢᴇɴᴇʀᴀʟ", "quiz:general"),
        ("🔬 ꜱᴄɪᴇɴᴄᴇ", "quiz:science"),
        ("📜 ʜɪꜱᴛᴏʀʏ", "quiz:history"),
        ("🗺️ ɢᴇᴏɢʀᴀᴘʜʏ", "quiz:geography"),
        ("🔢 ᴍᴀᴛʜꜱ", "quiz:maths"),
        ("💻 ᴛᴇᴄʜ", "quiz:tech"),
        ("⚽ ꜱᴘᴏʀᴛꜱ", "quiz:sports"),
        ("🎬 ᴍᴏᴠɪᴇꜱ", "quiz:movies"),
        ("🎵 ᴍᴜꜱɪᴄ", "quiz:music"),
        ("🐾 ᴀɴɪᴍᴀʟꜱ", "quiz:animals"),
        ("🍔 ꜰᴏᴏᴅ", "quiz:food"),
        ("📖 ʟɪᴛᴇʀᴀᴛᴜʀᴇ", "quiz:literature"),
        ("🏛️ ᴘᴏʟɪᴛɪᴄꜱ", "quiz:politics"),
        ("💰 ʙᴜꜱɪɴᴇꜱꜱ", "quiz:business"),
    ]
    rows = []
    for i in range(0, len(categories), 2):
        row = [
            InlineKeyboardButton(text=categories[i][0], callback_data=categories[i][1]),
        ]
        if i + 1 < len(categories):
            row.append(InlineKeyboardButton(text=categories[i + 1][0], callback_data=categories[i + 1][1]))
        rows.append(row)
    rows.append([InlineKeyboardButton(text="↩️ ʙᴀᴄᴋ", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def quiz_options_kb(qid, a, b, c, d):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"ᴀ) {a[:40]}", callback_data=f"qans:{qid}:A")],
        [InlineKeyboardButton(text=f"ʙ) {b[:40]}", callback_data=f"qans:{qid}:B")],
        [InlineKeyboardButton(text=f"ᴄ) {c[:40]}", callback_data=f"qans:{qid}:C")],
        [InlineKeyboardButton(text=f"ᴅ) {d[:40]}", callback_data=f"qans:{qid}:D")],
    ])


def leaderboard_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 ɢʀᴏᴜᴘ ᴛᴏᴘ 10", callback_data="lb:group")],
        [InlineKeyboardButton(text="↩️ ʙᴀᴄᴋ", callback_data="menu:main")],
    ])


def study_class_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📘 ᴄʟᴀꜱꜱ 10", callback_data="study:10"),
         InlineKeyboardButton(text="📗 ᴄʟᴀꜱꜱ 11", callback_data="study:11")],
        [InlineKeyboardButton(text="📕 ᴄʟᴀꜱꜱ 12", callback_data="study:12")],
        [InlineKeyboardButton(text="↩️ ʙᴀᴄᴋ", callback_data="menu:main")],
    ])


def study_class10_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔬 ꜱᴄɪᴇɴᴄᴇ", callback_data="st10:subject:science"),
         InlineKeyboardButton(text="📐 ᴍᴀᴛʜꜱ", callback_data="st10:subject:maths")],
        [InlineKeyboardButton(text="🌍 ꜱꜱᴛ", callback_data="st10:subject:sst"),
         InlineKeyboardButton(text="📖 ᴇɴɢʟɪꜱʜ", callback_data="st10:subject:english")],
        [InlineKeyboardButton(text="📝 ᴘʏǫ", callback_data="st10:section:pyq")],
        [InlineKeyboardButton(text="↩️ ʙᴀᴄᴋ", callback_data="menu:study")],
    ])


def study_class1112_kb(class_name):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 ᴊᴇᴇ", callback_data=f"st{class_name}:section:jee")],
        [InlineKeyboardButton(text="🩺 ɴᴇᴇᴛ", callback_data=f"st{class_name}:section:neet")],
        [InlineKeyboardButton(text="🎯🩺 ᴊᴇᴇ + ɴᴇᴇᴛ", callback_data=f"st{class_name}:section:both")],
        [InlineKeyboardButton(text="📝 ᴘʏǫꜱ", callback_data=f"st{class_name}:section:pyq")],
        [InlineKeyboardButton(text="↩️ ʙᴀᴄᴋ", callback_data="menu:study")],
    ])


def chapters_kb(class_name, section, chapters):
    rows = []
    for i, ch in enumerate(chapters):
        rows.append([InlineKeyboardButton(text=f"📄 {ch}", callback_data=f"stch:{class_name}:{section}:{i}")])
    rows.append([InlineKeyboardButton(text="↩️ ʙᴀᴄᴋ", callback_data="menu:study")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def shop_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👁️ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ᴄʜᴇᴄᴋᴇʀ (6💎)", callback_data="shop:checker")],
        [InlineKeyboardButton(text="⚡ xᴘ ʙᴏᴏꜱᴛ", callback_data="shop:xpboost")],
        [InlineKeyboardButton(text="↩️ ʙᴀᴄᴋ", callback_data="menu:main")],
    ])


def xpboost_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="5 ᴅᴀʏꜱ — 6💎", callback_data="shop:xp:5")],
        [InlineKeyboardButton(text="7 ᴅᴀʏꜱ — 8💎", callback_data="shop:xp:7")],
        [InlineKeyboardButton(text="12 ᴅᴀʏꜱ — 13💎", callback_data="shop:xp:12")],
        [InlineKeyboardButton(text="↩️ ʙᴀᴄᴋ", callback_data="shop:back")],
    ])


def premium_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 ᴍᴏɴᴛʜ — 90⭐", callback_data="prem:1m")],
        [InlineKeyboardButton(text="4 ᴍᴏɴᴛʜꜱ — 140⭐", callback_data="prem:4m")],
        [InlineKeyboardButton(text="12 ᴍᴏɴᴛʜꜱ — 175⭐", callback_data="prem:12m")],
        [InlineKeyboardButton(text="↩️ ʙᴀᴄᴋ", callback_data="menu:main")],
    ])
