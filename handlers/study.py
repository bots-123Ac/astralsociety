from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.main_menu import (
    study_class_kb, study_class10_kb, study_class1112_kb, chapters_kb,
    back_main_kb,
)
from utils.database import get_study_chapters, get_study_materials
from utils.ui import smart_edit

router = Router()

CHAPTER_CACHE = {}  # user_id -> list of chapters


@router.message(F.text.regexp(r"^/study(\s|$)"))
async def cmd_study(message: Message, state: FSMContext):
    if message.chat.type != "private":
        return await message.reply("📩 ᴜsє ᴛнis iη вσᴛ ᴅᴍ σηʟʏ.")
    await message.answer(
        "📚 <b>sᴛᴜᴅʏ ϻᴧтєʀiᴧʟ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "ᴄнσσsє ᴄʟᴧss:",
        reply_markup=study_class_kb()
    )


@router.callback_query(F.data == "menu:study")
async def cb_study(cb: CallbackQuery):
    await smart_edit(
        cb,
        "📚 <b>sᴛᴜᴅʏ ϻᴧтєʀiᴧʟ</b>\n━━━━━━━━━━━━━━━━━━━━━\n\nᴄнσσsє ᴄʟᴧss:",
        study_class_kb()
    )
    await cb.answer()


@router.callback_query(F.data == "study:10")
async def study_10(cb: CallbackQuery):
    await smart_edit(
        cb,
        "📘 <b>ᴄʟᴧss 10</b>\n━━━━━━━━━━━━━━━━━━━━━\n\nᴄнσσsє sєᴄтiση:",
        study_class10_kb()
    )
    await cb.answer()


@router.callback_query(F.data == "study:11")
async def study_11(cb: CallbackQuery):
    await smart_edit(
        cb,
        "📗 <b>ᴄʟᴧss 11</b>\n━━━━━━━━━━━━━━━━━━━━━\n\nᴄнσσsє sєᴄтiση:",
        study_class1112_kb(11)
    )
    await cb.answer()


@router.callback_query(F.data == "study:12")
async def study_12(cb: CallbackQuery):
    await smart_edit(
        cb,
        "📕 <b>ᴄʟᴧss 12</b>\n━━━━━━━━━━━━━━━━━━━━━\n\nᴄнσσsє sєᴄтiση:",
        study_class1112_kb(12)
    )
    await cb.answer()


@router.callback_query(F.data.startswith("st10:subject:"))
async def st10_subject(cb: CallbackQuery):
    subj = cb.data.split(":")[2]
    chapters = await get_study_chapters("10", "subject", subj)
    if not chapters:
        return await cb.answer(f"ησ ϻᴧтєʀiᴧʟ ʏєᴛ ғσʀ {subj}.", show_alert=True)
    CHAPTER_CACHE[cb.from_user.id] = chapters
    await smart_edit(
        cb,
        f"📘 <b>ᴄʟᴧss 10 — {subj.title()}</b>\n━━━━━━━━━━━━━━━━━━━━━\n\nᴄнσσsє ᴄнᴧᴩтєʀ:",
        chapters_kb("10", "subject", chapters, subj)
    )
    await cb.answer()


@router.callback_query(F.data.startswith("st10:section:"))
async def st10_pyq(cb: CallbackQuery):
    section = cb.data.split(":")[2]
    chapters = await get_study_chapters("10", section)
    if not chapters:
        return await cb.answer("ησ ϻᴧтєʀiᴧʟ ʏєт.", show_alert=True)
    CHAPTER_CACHE[cb.from_user.id] = chapters
    await smart_edit(
        cb,
        f"📝 <b>ᴄʟᴧss 10 — {section.upper()}</b>\n━━━━━━━━━━━━━━━━━━━━━\n\nᴄнσσsє ᴄнᴧᴩтєʀ:",
        chapters_kb("10", section, chapters)
    )
    await cb.answer()


@router.callback_query(F.data.startswith("st11:section:"))
async def st11_section(cb: CallbackQuery):
    section = cb.data.split(":")[2]
    chapters = await get_study_chapters("11", section)
    if not chapters:
        return await cb.answer("ησ ϻᴧтєʀiᴧʟ ʏєт.", show_alert=True)
    CHAPTER_CACHE[cb.from_user.id] = chapters
    await smart_edit(
        cb,
        f"📗 <b>ᴄʟᴧss 11 — {section.upper()}</b>\n━━━━━━━━━━━━━━━━━━━━━\n\nᴄнσσsє ᴄнᴧᴩтєʀ:",
        chapters_kb("11", section, chapters)
    )
    await cb.answer()


@router.callback_query(F.data.startswith("st12:section:"))
async def st12_section(cb: CallbackQuery):
    section = cb.data.split(":")[2]
    chapters = await get_study_chapters("12", section)
    if not chapters:
        return await cb.answer("ησ ϻᴧтєʀiᴧʟ ʏєт.", show_alert=True)
    CHAPTER_CACHE[cb.from_user.id] = chapters
    await smart_edit(
        cb,
        f"📕 <b>ᴄʟᴧss 12 — {section.upper()}</b>\n━━━━━━━━━━━━━━━━━━━━━\n\nᴄнσσsє ᴄнᴧᴩтєʀ:",
        chapters_kb("12", section, chapters)
    )
    await cb.answer()


@router.callback_query(F.data.startswith("stch:"))
async def st_chapter(cb: CallbackQuery):
    parts = cb.data.split(":")
    class_name = parts[1]
    section = parts[2]
    idx = int(parts[3])
    subject = parts[4] if len(parts) > 4 else None

    chapters = CHAPTER_CACHE.get(cb.from_user.id, [])
    if idx >= len(chapters):
        return await cb.answer("ᴄнᴧᴩтєʀ ησт ғσᴜηᴅ.", show_alert=True)
    chapter = chapters[idx]

    materials = await get_study_materials(class_name, section, chapter, subject)
    if not materials:
        return await cb.answer("ησ ғiʟєs ʏєт.", show_alert=True)

    await cb.message.edit_text(f"📄 <b>{chapter}</b> — {len(materials)} ғiʟє(s)", reply_markup=back_main_kb())
    for content_type, content, caption in materials:
        try:
            if content_type == "link":
                await cb.message.answer(f"🔗 {content}\n{caption or ''}")
            elif content_type == "video":
                await cb.message.answer_video(video=content, caption=caption or "")
            elif content_type == "photo":
                await cb.message.answer_photo(photo=content, caption=caption or "")
            else:
                await cb.message.answer_document(document=content, caption=caption or "")
        except Exception:
            pass
    await cb.answer()
