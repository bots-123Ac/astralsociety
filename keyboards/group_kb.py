from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def group_settings_kb(group_id: int, settings: dict):
    def btn(label, key):
        val = settings.get(key, 0)
        mark = "✅" if val else "❌"
        return InlineKeyboardButton(
            text=f"{mark} {label}", callback_data=f"grp:toggle:{key}"
        )

    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("ᴡᴇʟᴄᴏᴍᴇ", "welcome_enabled"),
         btn("ɢᴏᴏᴅʙʏᴇ", "goodbye_enabled")],
        [btn("ᴀɴᴛɪʟɪɴᴋ", "antilink"),
         btn("ᴀɴᴛɪғʟᴏᴏᴅ", "antiflood")],
        [btn("ᴀɴᴛɪғᴏʀᴡᴀʀᴅ", "antiforward"),
         btn("ᴄᴀᴘᴛᴄʜᴀ", "captcha")],
        [InlineKeyboardButton(text="🔒 ʟᴏᴄᴋs ᴍᴇɴᴜ", callback_data="grp:locks")],
    ])


def locks_menu_kb(locks: dict):
    def btn(lock_type):
        locked = locks.get(lock_type, 0)
        mark = "🔒" if locked else "🔓"
        label = lock_type.capitalize()
        return InlineKeyboardButton(
            text=f"{mark} {label}", callback_data=f"grp:lock:{lock_type}"
        )

    types = ["stickers", "gifs", "photos", "videos", "documents",
             "links", "audio", "voice", "polls", "games", "contacts", "forwards"]

    rows = []
    row = []
    for t in types:
        row.append(btn(t))
        if len(row) == 2:
            rows.append(row); row = []
    if row: rows.append(row)
    rows.append([InlineKeyboardButton(text="↩️ вᴀᴄᴋ", callback_data="grp:settings")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def group_help_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ sᴇᴛᴛɪɴɢs", callback_data="grp:settings")],
        [InlineKeyboardButton(text="🔒 ʟᴏᴄᴋs", callback_data="grp:locks")],
    ])
