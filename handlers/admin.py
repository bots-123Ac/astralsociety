from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.admin_kb import (
    admin_panel_kb, admin_edu_kb, admin_class_kb, admin_subject_kb,
)
from keyboards.main_menu import back_kb
from keyboards.study_kb import SUBJECTS
from utils.permissions import is_admin
from utils.database import save_material

router = Router()


class AdminUpload(StatesGroup):
    category = State()
    edu = State()
    cls = State()
    subject = State()
    chapter = State()
    file = State()


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ sσηʟʏ ᴧᴅϻiηs ᴄᴧη ᴜsє тнis ᴄσϻϻᴧηᴅ.")
        return
    text = (
        "👑 <b>ᴧᴅϻiη ᴩᴧηєʟ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "ᴡєʟᴄσϻє, ᴧᴅϻiη! ᴄнσσsє ᴧη ᴧᴄᴛiση:"
    )
    await message.answer(text, reply_markup=admin_panel_kb())


@router.callback_query(F.data.startswith("adm:add:"))
async def admin_add_category(cb: CallbackQuery, state: FSMContext):
    if not is_admin(cb.from_user.id):
        await cb.answer("❌ ᴧᴅϻiηs σηʟʏ", show_alert=True)
        return
    category = cb.data.split(":")[2]
    await state.update_data(category=category)
    await state.set_state(AdminUpload.edu)
    text = f"📚 ᴧᴅᴅiηɢ: <b>{category.upper()}</b>\n\nsєʟєᴄᴛ єᴅᴜᴄᴧᴛiση тʏᴩє:"
    await cb.message.edit_text(text, reply_markup=admin_edu_kb(category))
    await cb.answer()


@router.callback_query(F.data.startswith("admedu:"))
async def admin_pick_edu(cb: CallbackQuery, state: FSMContext):
    _, category, edu = cb.data.split(":")
    await state.update_data(edu=edu)
    if edu in ("jee", "neet"):
        # Skip class
        await state.update_data(cls="na")
        subjects = SUBJECTS.get((edu, "na"), [])
        await state.set_state(AdminUpload.subject)
        text = f"sєʟєᴄᴛ sᴜвᴊєᴄᴛ ({edu.upper()}):"
        await cb.message.edit_text(text, reply_markup=admin_subject_kb(category, edu, "na", subjects))
    else:
        await state.set_state(AdminUpload.cls)
        await cb.message.edit_text("sєʟєᴄᴛ ᴄʟᴧss:", reply_markup=admin_class_kb(category, edu))
    await cb.answer()


@router.callback_query(F.data.startswith("admcls:"))
async def admin_pick_class(cb: CallbackQuery, state: FSMContext):
    _, category, edu, cls = cb.data.split(":")
    await state.update_data(cls=cls)
    subjects = SUBJECTS.get((edu, cls), [])
    await state.set_state(AdminUpload.subject)
    text = f"sєʟєᴄᴛ sᴜвᴊєᴄᴛ (ᴄʟᴧss {cls}):"
    await cb.message.edit_text(text, reply_markup=admin_subject_kb(category, edu, cls, subjects))
    await cb.answer()


@router.callback_query(F.data.startswith("admsub:"))
async def admin_pick_subject(cb: CallbackQuery, state: FSMContext):
    parts = cb.data.split(":", 4)
    _, category, edu, cls, subject = parts
    await state.update_data(subject=subject)
    await state.set_state(AdminUpload.chapter)
    text = f"sᴜвᴊєᴄᴛ: <b>{subject}</b>\n\nsєηᴅ ᴄнᴧᴩᴛєʀ ηᴧϻє (тєxт ϻєssᴧɢє):"
    await cb.message.edit_text(text, reply_markup=back_kb("admin:cancel"))
    await cb.answer()


@router.message(AdminUpload.chapter)
async def admin_get_chapter(message: Message, state: FSMContext):
    await state.update_data(chapter=message.text.strip())
    await state.set_state(AdminUpload.file)
    await message.answer(
        f"ᴄнᴧᴩᴛєʀ: <b>{message.text}</b>\n\n"
        f"ησω sєηᴅ тнє ғiʟє (PDF / ᴅᴏᴄ / ᴠiᴅєᴏ) ᴡiᴛн σᴩᴛiσηᴧʟ ᴄᴧᴩᴛiση."
    )


@router.message(AdminUpload.file)
async def admin_get_file(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    file_id = None
    if message.document:
        file_id = message.document.file_id
    elif message.video:
        file_id = message.video.file_id
    elif message.photo:
        file_id = message.photo[-1].file_id
    else:
        await message.answer("❌ sєηᴅ ᴧ ғiʟє (ᴩᴅғ / ᴅσᴄ / ᴠiᴅєσ / ᴩнσᴛσ).")
        return

    data = await state.get_data()
    await save_material(
        data["category"], data["edu"], data["cls"],
        data["subject"], data["chapter"], file_id,
        message.caption or "", message.from_user.id
    )
    await state.clear()
    await message.answer(
        f"✅ <b>ᴜᴩʟσᴧᴅєᴅ!</b>\n\n"
        f"ᴄᴧᴛєɢσʀʏ: {data['category']}\n"
        f"єᴅᴜ: {data['edu'].upper()}\n"
        f"ᴄʟᴧss: {data['cls']}\n"
        f"sᴜвᴊєᴄᴛ: {data['subject']}\n"
        f"ᴄнᴧᴩᴛєʀ: {data['chapter']}",
        reply_markup=admin_panel_kb()
    )


@router.callback_query(F.data == "admin:cancel")
async def admin_cancel(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text("❌ ᴄᴧηᴄєʟʟєᴅ.", reply_markup=admin_panel_kb())
    await cb.answer()


@router.callback_query(F.data == "adm:delete")
async def admin_delete(cb: CallbackQuery):
    await cb.answer("🚧 ᴅєʟєᴛє ғєᴧᴛᴜʀє ᴄσϻiηɢ sσση", show_alert=True)
