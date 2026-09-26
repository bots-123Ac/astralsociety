from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.study_kb import (
    study_main_kb, education_type_kb, class_kb, subject_kb, chapter_kb,
    SUBJECTS,
)
from keyboards.main_menu import back_kb
from utils.database import get_materials

router = Router()


class StudyFlow(StatesGroup):
    browsing = State()


@router.callback_query(F.data == "menu:study")
async def show_study(cb: CallbackQuery):
    text = (
        "📚 <b>sᴛᴜᴅʏ sєᴄᴛiση</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "ᴡнᴧᴛ ᴅσ ʏσᴜ ᴡᴧηηᴧ sᴛᴜᴅʏ тσᴅᴧʏ?"
    )
    await cb.message.edit_text(text, reply_markup=study_main_kb())
    await cb.answer()


@router.callback_query(F.data.startswith("study:cat:"))
async def choose_category(cb: CallbackQuery):
    category = cb.data.split(":")[2]
    labels = {
        "notes": "📖 ησᴛєs", "dpp": "📝 ᴅᴩᴩ", "modules": "📚 ϻσᴅᴜʟєs",
        "books": "📕 вσσᴋs", "questions": "❓ ᴩʀᴧᴄᴛiᴄє", "quiz": "🧠 ǫᴜiᴢᴢєs",
    }
    text = (
        f"{labels.get(category, category)}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"sєʟєᴄᴛ єᴅᴜᴄᴧᴛiση тʏᴩє:"
    )
    await cb.message.edit_text(text, reply_markup=education_type_kb(category))
    await cb.answer()


@router.callback_query(F.data.startswith("edu:"))
async def choose_edu(cb: CallbackQuery):
    _, category, edu = cb.data.split(":")
    if edu in ("jee", "neet"):
        # Skip class, go to subject
        key = (edu, "na")
        subjects = SUBJECTS.get(key, [])
        text = f"📚 sєʟєᴄᴛ sᴜвᴊєᴄᴛ ({edu.upper()}):"
        await cb.message.edit_text(text, reply_markup=subject_kb(category, edu, "na"))
        await cb.answer()
        return

    text = "🏫 sєʟєᴄᴛ ᴄʟᴧss:"
    await cb.message.edit_text(text, reply_markup=class_kb(category, edu))
    await cb.answer()


@router.callback_query(F.data.startswith("cls:"))
async def choose_class(cb: CallbackQuery):
    _, category, edu, cls = cb.data.split(":")
    text = f"📚 sєʟєᴄᴛ sᴜвᴊєᴄᴛ (ᴄʟᴧss {cls}):"
    await cb.message.edit_text(text, reply_markup=subject_kb(category, edu, cls))
    await cb.answer()


@router.callback_query(F.data.startswith("sub:"))
async def choose_subject(cb: CallbackQuery):
    parts = cb.data.split(":", 4)
    _, category, edu, cls, subject = parts
    text = f"📖 sєʟєᴄᴛ ᴄнᴧᴩᴛєʀ ({subject}):"
    await cb.message.edit_text(text, reply_markup=chapter_kb(category, edu, cls, subject))
    await cb.answer()


@router.callback_query(F.data.startswith("chp:"))
async def show_chapter(cb: CallbackQuery):
    parts = cb.data.split(":", 5)
    _, category, edu, cls, subject, chapter = parts
    results = await get_materials(category, edu, cls, subject, chapter)

    if not results:
        text = (
            f"📭 <b>ησ ϻᴧᴛєʀiᴧʟ ғσᴜηᴅ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"ᴄᴧᴛєɢσʀʏ: {category}\n"
            f"єᴅᴜ: {edu.upper()}\n"
            f"ᴄʟᴧss: {cls}\n"
            f"sᴜвᴊєᴄᴛ: {subject}\n"
            f"ᴄнᴧᴩᴛєʀ: {chapter}\n\n"
            f"ᴧᴅϻiηs sє ϻᴧᴛєʀiᴧʟ ᴜᴩʟσᴧᴅ ηнi нᴜᴧ."
        )
        await cb.message.edit_text(text, reply_markup=back_kb("menu:study"))
        await cb.answer()
        return

    await cb.message.edit_text(
        f"📁 ᴍᴧᴛєʀiᴧʟs ғσᴜηᴅ: {len(results)}",
        reply_markup=back_kb("menu:study")
    )
    for file_id, caption in results:
        try:
            await cb.message.answer_document(document=file_id, caption=caption or "")
        except Exception:
            await cb.message.answer(f"📄 {caption or 'File'}\nFile ID: {file_id}")
    await cb.answer()
