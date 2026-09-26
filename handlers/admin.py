import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.admin_kb import (
    admin_panel_kb, admin_education_kb, admin_class_kb, admin_category_kb,
    admin_subject_kb, admin_resource_type_kb, admin_save_kb,
)
from keyboards.main_menu import back_kb
from utils.permissions import is_admin
from utils.database import save_resource
from utils.ui import smart_edit

router = Router()
logger = logging.getLogger(__name__)


class AdminUpload(StatesGroup):
    chapter = State()
    content = State()


def _parse_content(message: Message):
    """Return (content_type, content, caption) or (None, None, None)."""
    caption = message.caption or ""
    if message.document:
        return ("document", message.document.file_id, caption)
    if message.video:
        return ("video", message.video.file_id, caption)
    if message.photo:
        return ("photo", message.photo[-1].file_id, caption)
    if message.audio:
        return ("document", message.audio.file_id, caption)
    if message.text:
        text = message.text.strip()
        if text.startswith("http://") or text.startswith("https://") or text.startswith("tg://"):
            return ("link", text, "")
        return ("link", text, "")
    return (None, None, None)


# ─────────────── ENTRY ───────────────

@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("❌ sσηʟʏ ᴧᴅϻiηs ᴄᴧη ᴜsє тнis ᴄσϻϻᴧηᴅ.")
        return
    await state.clear()
    text = (
        "👑 <b>ᴧᴅϻiη ᴩᴧηєʟ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "ᴡєʟᴄσϻє, ᴧᴅϻiη! ᴄнσσsє ᴧη ᴧᴄᴛiση:"
    )
    await message.answer(text, reply_markup=admin_panel_kb())


@router.callback_query(F.data == "adm:add")
async def adm_add(cb: CallbackQuery, state: FSMContext):
    if not is_admin(cb.from_user.id):
        await cb.answer("❌ ᴧᴅϻiηs σηʟʏ", show_alert=True)
        return
    await state.clear()
    text = (
        "📚 <b>ᴧᴅᴅ ʀєsσᴜʀᴄє</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "sєʟєᴄᴛ єᴅᴜᴄᴧᴛiση тʏᴩє:"
    )
    await smart_edit(cb, text, admin_education_kb())
    await cb.answer()


@router.callback_query(F.data == "adm:manage")
async def adm_manage(cb: CallbackQuery):
    await cb.answer("🚧 ϻᴧηᴧɢє ғєᴧᴛᴜʀє ᴄσϻiηɢ sσση", show_alert=True)


# ─────────────── EDUCATION ───────────────

@router.callback_query(F.data.startswith("adm:edu:"))
async def adm_edu(cb: CallbackQuery, state: FSMContext):
    edu = cb.data.split(":")[2]
    await state.update_data(edu=edu, pending=[])
    if edu in ("jee", "neet"):
        await state.update_data(cls="na")
        await smart_edit(cb, "🔬 sєʟєᴄᴛ ᴄᴧᴛєɢσʀʏ:", admin_category_kb())
    else:
        await smart_edit(cb, "🏫 sєʟєᴄᴛ ᴄʟᴧss:", admin_class_kb())
    await cb.answer()


@router.callback_query(F.data.startswith("adm:cls:"))
async def adm_cls(cb: CallbackQuery, state: FSMContext):
    cls = cb.data.split(":")[2]
    await state.update_data(cls=cls)
    await smart_edit(cb, "🔬 sєʟєᴄᴛ ᴄᴧᴛєɢσʀʏ:", admin_category_kb())
    await cb.answer()


@router.callback_query(F.data.startswith("adm:cat:"))
async def adm_cat(cb: CallbackQuery, state: FSMContext):
    cat = cb.data.split(":")[2]
    await state.update_data(cat=cat)
    await smart_edit(cb, "📚 sєʟєᴄᴛ sᴜвᴊєᴄᴛ:", admin_subject_kb(cat))
    await cb.answer()


@router.callback_query(F.data.startswith("adm:sub:"))
async def adm_sub(cb: CallbackQuery, state: FSMContext):
    sub = cb.data.split(":", 2)[2]
    await state.update_data(sub=sub)
    await state.set_state(AdminUpload.chapter)
    text = (
        f"📚 sᴜвᴊєᴄᴛ: <b>{sub}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"sєηᴅ тнє ᴄнᴧᴩᴛєʀ ηᴧϻє (тєxт ϻєssᴧɢє):"
    )
    await smart_edit(cb, text, back_kb("adm:cancel"))
    await cb.answer()


# ─────────────── CHAPTER (text) ───────────────

@router.message(AdminUpload.chapter)
async def adm_chapter(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    chapter = message.text.strip()
    await state.update_data(chapter=chapter)
    text = (
        f"ᴄнᴧᴩᴛєʀ: <b>{chapter}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ᴡнᴧᴛ ᴅσ ʏσᴜ ᴡᴧηηᴧ ᴧᴅᴅ?"
    )
    await message.answer(text, reply_markup=admin_resource_type_kb())


# ─────────────── RESOURCE TYPE ───────────────

@router.callback_query(F.data.startswith("adm:rt:"))
async def adm_rt(cb: CallbackQuery, state: FSMContext):
    rt = cb.data.split(":")[2]
    await state.update_data(current_rt=rt)
    await state.set_state(AdminUpload.content)
    text = (
        "📤 <b>sєηᴅ тнє ʀєsσᴜʀᴄє</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "sєηᴅ ᴧ ʟiηᴋ, ᴩᴅғ, ᴠiᴅєσ, iϻᴧɢє σʀ ᴅσᴄᴜϻєηᴛ."
    )
    await smart_edit(cb, text, back_kb("adm:cancel"))
    await cb.answer()


# ─────────────── CONTENT (file / link) ───────────────

@router.message(AdminUpload.content)
async def adm_content(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    content_type, content, caption = _parse_content(message)
    if not content:
        await message.answer("❌ sєηᴅ ᴧ ʟiηᴋ σʀ ғiʟє.")
        return

    data = await state.get_data()
    rt = data.get("current_rt")
    pending = data.get("pending", [])
    pending.append({
        "resource_type": rt,
        "content_type": content_type,
        "content": content,
        "caption": caption,
    })
    await state.update_data(pending=pending)

    text = (
        f"✅ ɪᴛєϻ ᴧᴅᴅєᴅ: <b>{rt}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"sσ ғᴧʀ ᴧᴅᴅєᴅ: <b>{len(pending)}</b> ɪᴛєϻ(s)\n\n"
        f"ᴡнᴧᴛ ηєxᴛ?"
    )
    await message.answer(text, reply_markup=admin_save_kb())


# ─────────────── SAVE / ADD MORE / CANCEL ───────────────

@router.callback_query(F.data == "adm:save")
async def adm_save(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    pending = data.get("pending", [])
    if not pending:
        await cb.answer("ησ ɪᴛєϻs тσ sᴧᴠє.", show_alert=True)
        return

    for item in pending:
        await save_resource(
            data["edu"], data["cls"], data["cat"], data["sub"], data["chapter"],
            item["resource_type"], item["content_type"], item["content"],
            item["caption"], cb.from_user.id,
        )

    count = len(pending)
    await state.clear()
    text = (
        f"✅ <b>sᴧᴠєᴅ {count} ʀєsσᴜʀᴄє(s)!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ᴄнᴧᴩᴛєʀ: <b>{data['chapter']}</b>\n"
        f"sᴜвᴊєᴄᴛ: <b>{data['sub']}</b>\n\n"
        f"ɴᴏᴡ ᴜsєʀs ᴄᴀɴ sᴇᴇ ᴛʜᴇᴍ ɪɴ sᴛᴜᴅʏ sᴇᴄᴛɪᴏɴ."
    )
    await smart_edit(cb, text, admin_panel_kb())
    await cb.answer()


@router.callback_query(F.data == "adm:addmore")
async def adm_addmore(cb: CallbackQuery, state: FSMContext):
    text = "ᴡнᴧᴛ ᴅσ ʏσᴜ ᴡᴧηηᴧ ᴧᴅᴅ?"
    await smart_edit(cb, text, admin_resource_type_kb())
    await cb.answer()


@router.callback_query(F.data == "adm:cancel")
async def adm_cancel(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await smart_edit(cb, "❌ ᴄᴧηᴄєʟʟєᴅ.", admin_panel_kb())
    await cb.answer()
