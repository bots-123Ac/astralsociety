import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
)

try:
    from aiogram.dispatcher.event.bases import SkipHandler
except ImportError:
    class SkipHandler(Exception):
        pass

from config import BOT_NAME
from utils.permissions import is_bot_admin
from utils.database import save_study_material
from utils.ui import smart_edit

router = Router()
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════
# IN-MEMORY SESSIONS (per user)
# ═══════════════════════════════════════════════
SESSIONS = {}   # user_id -> {"step": str, "data": {...}}


def _clear(user_id):
    SESSIONS.pop(user_id, None)


# ═══════════════════════════════════════════════
# KEYBOARDS
# ═══════════════════════════════════════════════
def admin_panel_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 ᴧᴅᴅ sᴛᴜᴅʏ ϻᴧᴛєʀiᴧʟ", callback_data="adm:add")],
        [InlineKeyboardButton(text="📊 sᴛᴧᴛs", callback_data="adm:stats")],
        [InlineKeyboardButton(text="↩️ вᴧᴄᴋ", callback_data="menu:main")],
    ])


def class_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📘 ᴄʟᴧss 10", callback_data="adm:cls:10"),
         InlineKeyboardButton(text="📗 ᴄʟᴧss 11", callback_data="adm:cls:11")],
        [InlineKeyboardButton(text="📕 ᴄʟᴧss 12", callback_data="adm:cls:12")],
        [InlineKeyboardButton(text="❌ ᴄᴧηᴄєʟ", callback_data="adm:cancel")],
    ])


def section_10_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔬 sᴄiєηᴄє", callback_data="adm:sec:science"),
         InlineKeyboardButton(text="📐 ϻᴧᴛнs", callback_data="adm:sec:maths")],
        [InlineKeyboardButton(text="🌍 ssᴛ", callback_data="adm:sec:sst"),
         InlineKeyboardButton(text="📖 єηɢʟisн", callback_data="adm:sec:english")],
        [InlineKeyboardButton(text="📝 ᴩʏǫ", callback_data="adm:sec:pyq")],
        [InlineKeyboardButton(text="❌ ᴄᴧηᴄєʟ", callback_data="adm:cancel")],
    ])


def section_1112_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 ᴊєє", callback_data="adm:sec:jee")],
        [InlineKeyboardButton(text="🩺 ηєєᴛ", callback_data="adm:sec:neet")],
        [InlineKeyboardButton(text="🎯🩺 ᴊєє + ηєєᴛ", callback_data="adm:sec:both")],
        [InlineKeyboardButton(text="📝 ᴩʏǫs", callback_data="adm:sec:pyq")],
        [InlineKeyboardButton(text="❌ ᴄᴧηᴄєʟ", callback_data="adm:cancel")],
    ])


# ═══════════════════════════════════════════════
# /admin
# ═══════════════════════════════════════════════
@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_bot_admin(message.from_user.id):
        return await message.reply("❌ sσηʟʏ ᴧᴅϻiηs ᴄᴧη ᴜsє ᴛнis.")
    _clear(message.from_user.id)
    await message.answer(
        f"👑 <b>{BOT_NAME} — ᴧᴅϻiη ᴩᴧηєʟ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ᴄнσσsє ᴧη ᴧᴄᴛiση:",
        reply_markup=admin_panel_kb()
    )


@router.callback_query(F.data == "adm:cancel")
async def adm_cancel(cb: CallbackQuery):
    if not is_bot_admin(cb.from_user.id):
        return await cb.answer("❌ ᴧᴅϻiηs σηʟʏ", show_alert=True)
    _clear(cb.from_user.id)
    await smart_edit(cb, "❌ ᴄᴧηᴄєʟʟєᴅ.", admin_panel_kb())
    await cb.answer()


@router.callback_query(F.data == "adm:stats")
async def adm_stats(cb: CallbackQuery):
    if not is_bot_admin(cb.from_user.id):
        return await cb.answer("❌ ᴧᴅϻiηs σηʟʏ", show_alert=True)
    import aiosqlite
    from config import DB_PATH
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM study_materials") as cur:
            materials = (await cur.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM users") as cur:
            users = (await cur.fetchone())[0]
    await smart_edit(
        cb,
        f"📊 <b>sᴛᴧᴛs</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📚 sᴛᴜᴅʏ ϻᴧᴛєʀiᴧʟs: <b>{materials}</b>\n"
        f"👥 ᴛσᴛᴧʟ ᴜsєʀs: <b>{users}</b>",
        admin_panel_kb()
    )
    await cb.answer()


# ═══════════════════════════════════════════════
# ADD STUDY — STEP 1: Class
# ═══════════════════════════════════════════════
@router.callback_query(F.data == "adm:add")
async def adm_add(cb: CallbackQuery):
    if not is_bot_admin(cb.from_user.id):
        return await cb.answer("❌ ᴧᴅϻiηs σηʟʏ", show_alert=True)
    SESSIONS[cb.from_user.id] = {"step": "class", "data": {}}
    await smart_edit(
        cb,
        f"📤 <b>ᴧᴅᴅ sᴛᴜᴅʏ ϻᴧᴛєʀiᴧʟ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"sᴛєᴩ 1/5 — ᴄнσσsє ᴄʟᴧss:",
        class_kb()
    )
    await cb.answer()


@router.callback_query(F.data.startswith("adm:cls:"))
async def adm_class(cb: CallbackQuery):
    if not is_bot_admin(cb.from_user.id):
        return await cb.answer("❌ ᴧᴅϻiηs σηʟʏ", show_alert=True)
    cls = cb.data.split(":")[2]
    sess = SESSIONS.setdefault(cb.from_user.id, {"step": "class", "data": {}})
    sess["data"]["class_name"] = cls
    sess["step"] = "section"

    if cls == "10":
        await smart_edit(
            cb,
            f"📤 <b>ᴄʟᴧss 10</b>\n\nsᴛєᴩ 2/5 — ᴄнσσsє sєᴄᴛiση:",
            section_10_kb()
        )
    else:
        await smart_edit(
            cb,
            f"📤 <b>ᴄʟᴧss {cls}</b>\n\nsᴛєᴩ 2/5 — ᴄнσσsє sєᴄᴛiση:",
            section_1112_kb()
        )
    await cb.answer()


@router.callback_query(F.data.startswith("adm:sec:"))
async def adm_section(cb: CallbackQuery):
    if not is_bot_admin(cb.from_user.id):
        return await cb.answer("❌ ᴧᴅϻiηs σηʟʏ", show_alert=True)
    section = cb.data.split(":")[2]
    sess = SESSIONS.setdefault(cb.from_user.id, {"step": "section", "data": {}})
    sess["data"]["section"] = section
    cls = sess["data"].get("class_name")

    if cls == "10" and section in ("science", "maths", "sst", "english"):
        sess["step"] = "subject"
        await cb.message.answer(
            f"📤 <b>sᴛєᴩ 3/5</b> — sєηᴅ sᴜвᴊєᴄᴛ ηᴧϻє (ᴛєxᴛ):\n"
            f"ᴇxᴧϻᴩʟє: <code>Biology</code> σʀ <code>Algebra</code>"
        )
    else:
        sess["data"]["subject"] = ""
        sess["step"] = "chapter"
        await cb.message.answer(
            f"📤 <b>sᴛєᴩ 4/5</b> — sєηᴅ ᴄнᴧᴩᴛєʀ ηᴧϻє (ᴛєxᴛ):\n"
            f"ᴇxᴧϻᴩʟє: <code>Chapter 1: Life Processes</code>"
        )
    await cb.answer()


# ═══════════════════════════════════════════════
# STEP 3/4/5 — Handle admin's text/photo/doc
# ═══════════════════════════════════════════════
@router.message(F.text | F.photo | F.document | F.video)
async def adm_content_handler(message: Message):
    user_id = message.from_user.id
    sess = SESSIONS.get(user_id)

    # No session → pass to next router
    if not sess:
        raise SkipHandler()

    if not is_bot_admin(user_id):
        _clear(user_id)
        raise SkipHandler()

    step = sess.get("step")

    # ─── Step 3: Subject ───
    if step == "subject":
        if not message.text:
            return await message.reply("❌ sєηᴅ тєxᴛ σηʟʏ.")
        sess["data"]["subject"] = message.text.strip()
        sess["step"] = "chapter"
        return await message.answer(
            f"📤 <b>sᴛєᴩ 4/5</b> — sєηᴅ ᴄнᴧᴩᴛєʀ ηᴧϻє (ᴛєxᴛ):\n"
            f"ᴇxᴧϻᴩʟє: <code>Chapter 1: Life Processes</code>"
        )

    # ─── Step 4: Chapter ───
    if step == "chapter":
        if not message.text:
            return await message.reply("❌ sєηᴅ тєxᴛ σηʟʏ.")
        sess["data"]["chapter"] = message.text.strip()
        sess["step"] = "content"
        return await message.answer(
            f"📤 <b>sᴛєᴩ 5/5</b> — sєηᴅ тнє ϻᴧᴛєʀiᴧʟ:\n"
            f"📄 PDF | 🎥 ᴠiᴅєσ | 🖼️ ᴩнσᴛσ | 🔗 ʟiηᴋ"
        )

    # ─── Step 5: Content (file/link) ───
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
            return await message.reply("❌ sєηᴅ PDF/ᴠiᴅєσ/ᴩнσᴛσ σʀ ᴠᴧʟiᴅ ʟiηᴋ.")

        data = sess["data"]
        await save_study_material(
            data["class_name"],
            data["section"],
            data.get("subject", ""),
            data["chapter"],
            ctype,
            content,
            message.caption or "",
            user_id,
        )
        _clear(user_id)
        return await message.answer(
            f"✅ <b>ϻᴧᴛєʀiᴧʟ sᴧᴠєᴅ!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📘 ᴄʟᴧss: <b>{data['class_name']}</b>\n"
            f"📂 sєᴄᴛiση: <b>{data['section']}</b>\n"
            f"📚 sᴜвᴊєᴄᴛ: <b>{data.get('subject') or '—'}</b>\n"
            f"📄 ᴄнᴧᴩᴛєʀ: <b>{data['chapter']}</b>\n\n"
            f"ᴜsєʀs ᴄᴧη ησω ᴧᴄᴄєss iᴛ ᴠiᴧ /study.",
            reply_markup=admin_panel_kb()
        )

    # Unknown step → skip
    raise SkipHandler()
