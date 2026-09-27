import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import BOT_NAME
from keyboards.main_menu import back_main_kb
from utils.permissions import is_bot_admin
from utils.database import save_study_material
from utils.ui import smart_edit

router = Router()
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════
# FSM STATES
# ═══════════════════════════════════════════════
class AdminUpload(StatesGroup):
    class_name = State()
    section = State()
    subject = State()
    chapter = State()
    content = State()


# ═══════════════════════════════════════════════
# KEYBOARDS
# ═══════════════════════════════════════════════
def admin_panel_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 ᴧᴅᴅ sᴛᴜᴅʏ ϻᴧᴛᴇʀɪᴧʟ", callback_data="adm:add")],
        [InlineKeyboardButton(text="📝 ᴧᴅᴅ ǫᴜɪᴢ ǫᴜᴇsᴛɪᴏη", callback_data="adm:quiz")],
        [InlineKeyboardButton(text="📊 sᴛᴧᴛs", callback_data="adm:stats")],
        [InlineKeyboardButton(text="↩️ ᴠᴧᴄᴋ", callback_data="menu:main")],
    ])


def class_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📘 ᴄʟᴧss 10", callback_data="adm:cls:10"),
         InlineKeyboardButton(text="📗 ᴄʟᴧss 11", callback_data="adm:cls:11")],
        [InlineKeyboardButton(text="📕 ᴄʟᴧss 12", callback_data="adm:cls:12")],
        [InlineKeyboardButton(text="❌ ᴄᴧηᴄᴇʟ", callback_data="adm:cancel")],
    ])


def section_10_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔬 sᴄɪєηᴄє", callback_data="adm:sec:science"),
         InlineKeyboardButton(text="📐 ϻᴧᴛʜs", callback_data="adm:sec:maths")],
        [InlineKeyboardButton(text="🌍 sst", callback_data="adm:sec:sst"),
         InlineKeyboardButton(text="📖 єηɢʟɪsʜ", callback_data="adm:sec:english")],
        [InlineKeyboardButton(text="📝 ᴘʏǫ", callback_data="adm:sec:pyq")],
        [InlineKeyboardButton(text="❌ ᴄᴧηᴄᴇʟ", callback_data="adm:cancel")],
    ])


def section_1112_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 ᴊєє", callback_data="adm:sec:jee")],
        [InlineKeyboardButton(text="🩺 ηєєᴛ", callback_data="adm:sec:neet")],
        [InlineKeyboardButton(text="🎯🩺 ᴊєє + ηєєᴛ", callback_data="adm:sec:both")],
        [InlineKeyboardButton(text="📝 ᴘʏǫs", callback_data="adm:sec:pyq")],
        [InlineKeyboardButton(text="❌ ᴄᴧηᴄᴇʟ", callback_data="adm:cancel")],
    ])


# ═══════════════════════════════════════════════
# ENTRY
# ═══════════════════════════════════════════════
@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    if not is_bot_admin(message.from_user.id):
        return await message.reply("❌ sσηʟʏ ᴧᴅϻɪηs ᴄᴧη ᴜsє ᴛнɪs ᴄσϻϻᴧηᴅ.")
    await state.clear()
    await message.answer(
        f"👑 <b>{BOT_NAME} — ᴧᴅϻɪη ᴘᴧηєʟ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ᴄнσσsє ᴧη ᴧᴄᴛɪση:",
        reply_markup=admin_panel_kb()
    )


@router.callback_query(F.data == "adm:cancel")
async def adm_cancel(cb: CallbackQuery, state: FSMContext):
    if not is_bot_admin(cb.from_user.id):
        return await cb.answer("❌ ᴧᴅϻɪηs σηʟʏ", show_alert=True)
    await state.clear()
    await smart_edit(cb, "❌ ᴄᴧηᴄᴇʟʟєᴅ.", admin_panel_kb())
    await cb.answer()


@router.callback_query(F.data == "adm:stats")
async def adm_stats(cb: CallbackQuery):
    if not is_bot_admin(cb.from_user.id):
        return await cb.answer("❌ ᴧᴅϻɪηs σηʟʏ", show_alert=True)

    import aiosqlite
    from config import DB_PATH
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM study_materials") as cur:
            materials = (await cur.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM users") as cur:
            users = (await cur.fetchone())[0]

    await smart_edit(
        cb,
        f"📊 <b>ʙσᴛ sᴛᴧᴛs</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📚 sᴛᴜᴅʏ ϻᴧᴛᴇʀɪᴧʟs: <b>{materials}</b>\n"
        f"👥 ᴛσᴛᴧʟ ᴜsᴇʀs: <b>{users}</b>",
        admin_panel_kb()
    )
    await cb.answer()


# ═══════════════════════════════════════════════
# 📤 ADD STUDY MATERIAL FLOW
# ═══════════════════════════════════════════════
@router.callback_query(F.data == "adm:add")
async def adm_add(cb: CallbackQuery, state: FSMContext):
    if not is_bot_admin(cb.from_user.id):
        return await cb.answer("❌ ᴧᴅϻɪηs σηʟʏ", show_alert=True)
    await state.clear()
    await state.set_state(AdminUpload.class_name)
    await smart_edit(
        cb,
        f"📤 <b>ᴧᴅᴅ sᴛᴜᴅʏ ϻᴧᴛᴇʀɪᴧʟ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"sᴛᴇᴩ 1/5 — ᴄнσσsє ᴄʟᴧss:",
        class_kb()
    )
    await cb.answer()


@router.callback_query(F.data.startswith("adm:cls:"), AdminUpload.class_name)
async def adm_class(cb: CallbackQuery, state: FSMContext):
    cls = cb.data.split(":")[2]
    await state.update_data(class_name=cls)

    if cls == "10":
        await state.set_state(AdminUpload.section)
        await smart_edit(
            cb,
            f"📤 <b>ᴧᴅᴅ sᴛᴜᴅʏ ϻᴧᴛᴇʀɪᴧʟ — ᴄʟᴧss 10</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"sᴛᴇᴩ 2/5 — ᴄнσσsє sєᴄᴛɪση:",
            section_10_kb()
        )
    else:
        await state.set_state(AdminUpload.section)
        await smart_edit(
            cb,
            f"📤 <b>ᴧᴅᴅ sᴛᴜᴅʏ ϻᴧᴛᴇʀɪᴧʟ — ᴄʟᴧss {cls}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"sᴛᴇᴩ 2/5 — ᴄнσσsє sєᴄᴛɪση:",
            section_1112_kb()
        )
    await cb.answer()


@router.callback_query(F.data.startswith("adm:sec:"), AdminUpload.section)
async def adm_section(cb: CallbackQuery, state: FSMContext):
    section = cb.data.split(":")[2]
    await state.update_data(section=section)

    data = await state.get_data()
    cls = data.get("class_name")

    # Subject only for class 10 subjects (not for JEE/NEET/PYQ)
    if cls == "10" and section in ("science", "maths", "sst", "english"):
        await state.set_state(AdminUpload.subject)
        await cb.message.answer(
            f"sᴛᴇᴩ 3/5 — sєηᴅ sᴜʙᴊєᴄᴛ ηᴧϻє (ᴛєxᴛ):\n"
            f"ᴇxᴧϻᴩʟє: <code>Biology</code> σʀ <code>Algebra</code>"
        )
    else:
        # No subject step — skip to chapter
        await state.update_data(subject="")
        await state.set_state(AdminUpload.chapter)
        await cb.message.answer(
            f"sᴛᴇᴩ 4/5 — sєηᴅ ᴄнᴧᴩᴛєʀ ηᴧᴍє (ᴛєxᴛ):\n"
            f"ᴇxᴧϻᴩʟє: <code>Chapter 1: Life Processes</code>"
        )
    await cb.answer()


@router.message(AdminUpload.subject)
async def adm_subject(message: Message, state: FSMContext):
    if not is_bot_admin(message.from_user.id):
        return
    await state.update_data(subject=message.text.strip())
    await state.set_state(AdminUpload.chapter)
    await message.answer(
        f"sᴛᴇᴩ 4/5 — sєηᴅ ᴄнᴧᴩᴛєʀ ηᴧᴍє (ᴛєxᴛ):\n"
        f"ᴇxᴧϻᴩʟє: <code>Chapter 1: Life Processes</code>"
    )


@router.message(AdminUpload.chapter)
async def adm_chapter(message: Message, state: FSMContext):
    if not is_bot_admin(message.from_user.id):
        return
    await state.update_data(chapter=message.text.strip())
    await state.set_state(AdminUpload.content)
    await message.answer(
        f"sᴛᴇᴩ 5/5 — sєηᴅ ᴛнє ϻᴧᴛᴇʀɪᴧʟ\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📄 PDF | 🎥 Video | 🖼️ Photo | 🔗 Link | 📁 Document"
    )


@router.message(AdminUpload.content)
async def adm_content(message: Message, state: FSMContext):
    if not is_bot_admin(message.from_user.id):
        return

    # Detect content type
    if message.document:
        ctype, content = "document", message.document.file_id
    elif message.video:
        ctype, content = "video", message.video.file_id
    elif message.photo:
        ctype, content = "photo", message.photo[-1].file_id
    elif message.text:
        ctype, content = "link", message.text.strip()
    else:
        return await message.reply("❌ sєηᴅ ᴧ PDF, ᴠɪᴅєσ, ᴩнσᴛσ σʀ ʟɪηᴋ.")

    data = await state.get_data()
    caption = message.caption or ""

    await save_study_material(
        data["class_name"],
        data["section"],
        data.get("subject", ""),
        data["chapter"],
        ctype,
        content,
        caption,
        message.from_user.id,
    )
    await state.clear()

    await message.answer(
        f"✅ <b>ᴍᴧᴛᴇʀɪᴧʟ sᴧᴠᴇᴅ!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📘 ᴄʟᴧss: <b>{data['class_name']}</b>\n"
        f"📂 sєᴄᴛɪση: <b>{data['section']}</b>\n"
        f"📚 sᴜʙᴊєᴄᴛ: <b>{data.get('subject') or '—'}</b>\n"
        f"📄 ᴄнᴧᴩᴛєʀ: <b>{data['chapter']}</b>\n\n"
        f"ᴜsᴇʀs ᴄᴧη ησω ᴧᴄᴄєss ɪᴛ ᴠɪᴧ /study.",
        reply_markup=admin_panel_kb()
    )


# ═══════════════════════════════════════════════
# 📝 ADD QUIZ QUESTION
# ═══════════════════════════════════════════════
@router.callback_query(F.data == "adm:quiz")
async def adm_quiz(cb: CallbackQuery):
    if not is_bot_admin(cb.from_user.id):
        return await cb.answer("❌ ᴧᴅϻɪηs σηʟʏ", show_alert=True)
    await cb.message.answer(
        f"📝 <b>ᴧᴅᴅ ǫᴜɪᴢ ǫᴜᴇsᴛɪᴏη</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ᴜsє ᴛнɪs ғσʀϻᴧᴛ (ᴛєxᴛ ϻєssᴧɢє):\n\n"
        f"<code>SPACE|Question here|A|B|C|D|B</code>\n\n"
        f"• First word: <b>SPACE</b> or <b>GENERAL</b>\n"
        f"• Then: question\n"
        f"• 4 options\n"
        f"• Correct answer (A/B/C/D)"
    )
    await cb.answer()


@router.message(F.text.regexp(r"^(SPACE|GENERAL)\|"))
async def adm_quiz_add(message: Message):
    if not is_bot_admin(message.from_user.id):
        return
    parts = message.text.split("|")
    if len(parts) != 7:
        return await message.reply("❌ ғσʀϻᴧᴛ: <code>SPACE|Q|A|B|C|D|Correct</code>")

    cat = parts[0].strip().upper()
    question = parts[1].strip()
    a, b, c, d = parts[2].strip(), parts[3].strip(), parts[4].strip(), parts[5].strip()
    correct = parts[6].strip().upper()

    if correct not in ("A", "B", "C", "D"):
        return await message.reply("❌ ᴄσʀʀєᴄᴛ ϻᴜsᴛ вє A/B/C/D.")

    # Save to database
    import aiosqlite
    from config import DB_PATH
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO quiz_questions
            (category, question, option_a, option_b, option_c, option_d, correct)
            VALUES (?,?,?,?,?,?,?)""",
            (cat, question, a, b, c, d, correct)
        )
        await db.commit()

    await message.reply(
        f"✅ <b>ǫᴜɪᴢ ǫᴜєsᴛɪση ᴧᴅᴅєᴅ!</b>\n\n"
        f"ᴄᴧᴛєɢσʀʏ: {cat}\n"
        f"ǫᴜєsᴛɪση: {question[:60]}...\n"
        f"ᴄσʀʀєᴄᴛ: {correct}"
    )
