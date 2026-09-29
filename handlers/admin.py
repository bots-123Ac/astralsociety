import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
)

from config import BOT_NAME
from utils.permissions import is_bot_admin
from utils.database import save_study_material

router = Router()
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════
# SESSIONS — user_id -> {step, data}
# ═══════════════════════════════════════════════
SESSIONS = {}


def _clear(user_id):
    SESSIONS.pop(user_id, None)


def admin_panel_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 ᴀᴅᴅ ꜱᴛᴜᴅʏ ᴍᴀᴛᴇʀɪᴀʟ", callback_data="adm:add")],
        [InlineKeyboardButton(text="↩️ ʙᴀᴄᴋ", callback_data="menu:main")],
    ])


def class_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📘 ᴄʟᴀꜱꜱ 10", callback_data="adm:cls:10"),
         InlineKeyboardButton(text="📗 ᴄʟᴀꜱꜱ 11", callback_data="adm:cls:11")],
        [InlineKeyboardButton(text="📕 ᴄʟᴀꜱꜱ 12", callback_data="adm:cls:12")],
        [InlineKeyboardButton(text="↩️ ʙᴀᴄᴋ", callback_data="adm:panel")],
    ])


def section_10_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔬 ꜱᴄɪᴇɴᴄᴇ", callback_data="adm:sec:science"),
         InlineKeyboardButton(text="📐 ᴍᴀᴛʜꜱ", callback_data="adm:sec:maths")],
        [InlineKeyboardButton(text="🌍 ꜱꜱᴛ", callback_data="adm:sec:sst"),
         InlineKeyboardButton(text="📖 ᴇɴɢʟɪꜱʜ", callback_data="adm:sec:english")],
        [InlineKeyboardButton(text="📝 ᴘʏǫ", callback_data="adm:sec:pyq")],
        [InlineKeyboardButton(text="↩️ ʙᴀᴄᴋ", callback_data="adm:add")],
    ])


def section_1112_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 ᴊᴇᴇ", callback_data="adm:sec:jee")],
        [InlineKeyboardButton(text="🩺 ɴᴇᴇᴛ", callback_data="adm:sec:neet")],
        [InlineKeyboardButton(text="🎯🩺 ᴊᴇᴇ + ɴᴇᴇᴛ", callback_data="adm:sec:both")],
        [InlineKeyboardButton(text="📝 ᴘʏǫꜱ", callback_data="adm:sec:pyq")],
        [InlineKeyboardButton(text="↩️ ʙᴀᴄᴋ", callback_data="adm:add")],
    ])


# ═══════════════════════════════════════════════
# /admin
# ═══════════════════════════════════════════════
@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_bot_admin(message.from_user.id):
        return await message.reply("❌ ꜱᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ.")
    _clear(message.from_user.id)
    await message.answer(
        f"👑 <b>{BOT_NAME} — ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\nᴄʜᴏᴏꜱᴇ ᴀɴ ᴀᴄᴛɪᴏɴ:",
        reply_markup=admin_panel_kb()
    )


@router.callback_query(F.data == "adm:panel")
async def adm_panel(cb: CallbackQuery):
    if not is_bot_admin(cb.from_user.id):
        return await cb.answer("❌", show_alert=True)
    _clear(cb.from_user.id)
    await cb.message.edit_text(
        f"👑 <b>{BOT_NAME} — ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\nᴄʜᴏᴏꜱᴇ ᴀɴ ᴀᴄᴛɪᴏɴ:",
        reply_markup=admin_panel_kb()
    )
    await cb.answer()


@router.callback_query(F.data == "adm:add")
async def adm_add(cb: CallbackQuery):
    if not is_bot_admin(cb.from_user.id):
        return await cb.answer("❌", show_alert=True)
    SESSIONS[cb.from_user.id] = {"step": "class", "data": {}}
    await cb.message.edit_text(
        "📤 <b>ᴀᴅᴅ ꜱᴛᴜᴅʏ ᴍᴀᴛᴇʀɪᴀʟ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\nꜱᴛᴇᴘ 1/5 — ᴄʜᴏᴏꜱᴇ ᴄʟᴀꜱꜱ:",
        reply_markup=class_kb()
    )
    await cb.answer()


@router.callback_query(F.data.startswith("adm:cls:"))
async def adm_class(cb: CallbackQuery):
    if not is_bot_admin(cb.from_user.id):
        return await cb.answer("❌", show_alert=True)
    cls = cb.data.split(":")[2]
    sess = SESSIONS.setdefault(cb.from_user.id, {"step": "class", "data": {}})
    sess["data"]["class_name"] = cls
    sess["step"] = "section"

    if cls == "10":
        await cb.message.edit_text(
            f"📤 <b>ᴄʟᴀꜱꜱ 10</b>\n\nꜱᴛᴇᴘ 2/5 — ᴄʜᴏᴏꜱᴇ ꜱᴇᴄᴛɪᴏɴ:",
            reply_markup=section_10_kb()
        )
    else:
        await cb.message.edit_text(
            f"📤 <b>ᴄʟᴀꜱꜱ {cls}</b>\n\nꜱᴛᴇᴘ 2/5 — ᴄʜᴏᴏꜱᴇ ꜱᴇᴄᴛɪᴏɴ:",
            reply_markup=section_1112_kb()
        )
    await cb.answer()


@router.callback_query(F.data.startswith("adm:sec:"))
async def adm_section(cb: CallbackQuery):
    if not is_bot_admin(cb.from_user.id):
        return await cb.answer("❌", show_alert=True)
    section = cb.data.split(":")[2]
    sess = SESSIONS.setdefault(cb.from_user.id, {"step": "section", "data": {}})
    sess["data"]["section"] = section
    cls = sess["data"].get("class_name")

    if cls == "10" and section in ("science", "maths", "sst", "english"):
        sess["step"] = "subject"
        await cb.message.answer(
            "📤 <b>ꜱᴛᴇᴘ 3/5</b> — ꜱᴇɴᴅ ꜱᴜʙᴊᴇᴄᴛ ɴᴀᴍᴇ (ᴛᴇxᴛ):\n"
            "ᴇxᴀᴍᴘʟᴇ: <code>Biology</code>"
        )
    else:
        sess["data"]["subject"] = ""
        sess["step"] = "chapter"
        await cb.message.answer(
            "📤 <b>ꜱᴛᴇᴘ 4/5</b> — ꜱᴇɴᴅ ᴄʜᴀᴘᴛᴇʀ ɴᴀᴍᴇ (ᴛᴇxᴛ):\n"
            "ᴇxᴀᴍᴘʟᴇ: <code>Chapter 1: Life Processes</code>"
        )
    await cb.answer()


# ═══════════════════════════════════════════════
# TEXT / FILE — Only process if user in SESSIONS
# (checks SESSIONS dict directly, no filter needed)
# ═══════════════════════════════════════════════
@router.message(F.text | F.photo | F.document | F.video)
async def adm_content_handler(message: Message):
    user_id = message.from_user.id if message.from_user else 0

    # ⚠️ CRITICAL: If user NOT in SESSIONS, silently skip
    if user_id not in SESSIONS:
        return

    if not is_bot_admin(user_id):
        _clear(user_id)
        return

    sess = SESSIONS[user_id]
    step = sess.get("step")

    if step == "subject":
        if not message.text:
            return await message.reply("❌ ꜱᴇɴᴅ ᴛᴇxᴛ ᴏɴʟʏ.")
        sess["data"]["subject"] = message.text.strip()
        sess["step"] = "chapter"
        return await message.answer(
            "📤 <b>ꜱᴛᴇᴘ 4/5</b> — ꜱᴇɴᴅ ᴄʜᴀᴘᴛᴇʀ ɴᴀᴍᴇ (ᴛᴇxᴛ):\n"
            "ᴇxᴀᴍᴘʟᴇ: <code>Chapter 1: Life Processes</code>"
        )

    if step == "chapter":
        if not message.text:
            return await message.reply("❌ ꜱᴇɴᴅ ᴛᴇxᴛ ᴏɴʟʏ.")
        sess["data"]["chapter"] = message.text.strip()
        sess["step"] = "content"
        return await message.answer(
            "📤 <b>ꜱᴛᴇᴘ 5/5</b> — ꜱᴇɴᴅ ᴛʜᴇ ᴍᴀᴛᴇʀɪᴀʟ:\n"
            "📄 PDF | 🎥 ᴠɪᴅᴇᴏ | 🖼️ ᴘʜᴏᴛᴏ | 🔗 ʟɪɴᴋ"
        )

    if step == "content":
        ctype, content = None, None
        if message.document:
            ctype, content = "document", message.document.file_id
        elif message.video:
            ctype, content = "video", message.video.file_id
        elif message.photo:
            ctype, content = "photo", message.photo[-1].file_id
        elif message.text and (message.text.startswith("http") or "t.me/" in message.text):
            ctype, content = "link", message.text.strip()

        if not content:
            return await message.reply("❌ ꜱᴇɴᴅ PDF/ᴠɪᴅᴇᴏ/ᴘʜᴏᴛᴏ ᴏʀ ᴠᴀʟɪᴅ ʟɪɴᴋ.")

        data = sess["data"]
        subj = data.get("subject", "")
        chapter_final = f"{subj} — {data['chapter']}" if subj else data["chapter"]

        await save_study_material(
            data["class_name"],
            data["section"],
            "",
            chapter_final,
            ctype,
            content,
            message.caption or "",
            user_id,
        )
        _clear(user_id)
        return await message.answer(
            f"✅ <b>ᴍᴀᴛᴇʀɪᴀʟ ꜱᴀᴠᴇᴅ!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📘 ᴄʟᴀꜱꜱ: <b>{data['class_name']}</b>\n"
            f"📂 ꜱᴇᴄᴛɪᴏɴ: <b>{data['section']}</b>\n"
            f"📄 ᴄʜᴀᴘᴛᴇʀ: <b>{chapter_final}</b>\n\n"
            f"ᴜꜱᴇʀꜱ ᴄᴀɴ ɴᴏᴡ ᴀᴄᴄᴇꜱꜱ ᴠɪᴀ /study.",
            reply_markup=admin_panel_kb()
        )
