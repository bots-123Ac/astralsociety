from aiogram import Router, F
from aiogram.types import CallbackQuery, Message

from keyboards.main_menu import (
    study_class_kb, study_class10_kb, study_class1112_kb, chapters_kb,
    back_main_kb, back_kb,
)
from utils.database import get_study_chapters, get_study_materials

router = Router()

CHAPTER_CACHE = {}


@router.message(F.text.regexp(r"^/study(@\w+)?(\s|$)"))
async def cmd_study(message: Message):
    if message.chat.type != "private":
        return await message.reply("📩 ᴜꜱᴇ /study ɪɴ ʙᴏᴛ ᴅᴍ ᴏɴʟʏ.")
    await message.answer(
        "📚 <b>ꜱᴛᴜᴅʏ ᴍᴀᴛᴇʀɪᴀʟ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\nᴄʜᴏᴏꜱᴇ ᴄʟᴀꜱꜱ:",
        reply_markup=study_class_kb()
    )


@router.callback_query(F.data == "menu:study")
async def cb_study(cb: CallbackQuery):
    await cb.message.edit_text(
        "📚 <b>ꜱᴛᴜᴅʏ ᴍᴀᴛᴇʀɪᴀʟ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\nᴄʜᴏᴏꜱᴇ ᴄʟᴀꜱꜱ:",
        reply_markup=study_class_kb()
    )
    await cb.answer()


@router.callback_query(F.data == "study:10")
async def study_10(cb: CallbackQuery):
    await cb.message.edit_text(
        "📘 <b>ᴄʟᴀꜱꜱ 10</b>\n━━━━━━━━━━━━━━━━━━━━━\n\nᴄʜᴏᴏꜱᴇ ꜱᴇᴄᴛɪᴏɴ:",
        reply_markup=study_class10_kb()
    )
    await cb.answer()


@router.callback_query(F.data == "study:11")
async def study_11(cb: CallbackQuery):
    await cb.message.edit_text(
        "📗 <b>ᴄʟᴀꜱꜱ 11</b>\n━━━━━━━━━━━━━━━━━━━━━\n\nᴄʜᴏᴏꜱᴇ ꜱᴇᴄᴛɪᴏɴ:",
        reply_markup=study_class1112_kb(11)
    )
    await cb.answer()


@router.callback_query(F.data == "study:12")
async def study_12(cb: CallbackQuery):
    await cb.message.edit_text(
        "📕 <b>ᴄʟᴀꜱꜱ 12</b>\n━━━━━━━━━━━━━━━━━━━━━\n\nᴄʜᴏᴏꜱᴇ ꜱᴇᴄᴛɪᴏɴ:",
        reply_markup=study_class1112_kb(12)
    )
    await cb.answer()


# ═══ LEVEL 3: Chapter list for Class 10 subject ═══
@router.callback_query(F.data.startswith("st10:subject:"))
async def st10_subject(cb: CallbackQuery):
    section = cb.data.split(":")[2]
    chapters = await get_study_chapters("10", section)
    if not chapters:
        return await cb.answer("ησ ϻᴧᴛєʀiᴧʟ ʏєᴛ.", show_alert=True)
    CHAPTER_CACHE[cb.from_user.id] = chapters
    await cb.message.edit_text(
        f"📘 <b>ᴄʟᴀꜱꜱ 10 — {section.title()}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\nᴄʜᴏᴏꜱᴇ ᴄʜᴀᴘᴛᴇʀ:",
        reply_markup=chapters_kb("10", section, chapters)
    )
    await cb.answer()


@router.callback_query(F.data.startswith("st10:section:"))
async def st10_pyq(cb: CallbackQuery):
    section = cb.data.split(":")[2]
    chapters = await get_study_chapters("10", section)
    if not chapters:
        return await cb.answer("ησ ϻᴧᴛєʀiᴧʟ ʏєᴛ.", show_alert=True)
    CHAPTER_CACHE[cb.from_user.id] = chapters
    await cb.message.edit_text(
        f"📝 <b>ᴄʟᴀꜱꜱ 10 — {section.upper()}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\nᴄʜᴏᴏꜱᴇ ᴄʜᴀᴘᴛᴇʀ:",
        reply_markup=chapters_kb("10", section, chapters)
    )
    await cb.answer()


# ═══ LEVEL 3: Chapter list for Class 11 ═══
@router.callback_query(F.data.startswith("st11:section:"))
async def st11_section(cb: CallbackQuery):
    section = cb.data.split(":")[2]
    chapters = await get_study_chapters("11", section)
    if not chapters:
        return await cb.answer("ησ ϻᴧᴛєʀiᴧʟ ʏєᴛ.", show_alert=True)
    CHAPTER_CACHE[cb.from_user.id] = chapters
    await cb.message.edit_text(
        f"📗 <b>ᴄʟᴀꜱꜱ 11 — {section.upper()}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\nᴄʜᴏᴏꜱᴇ ᴄʜᴀᴘᴛᴇʀ:",
        reply_markup=chapters_kb("11", section, chapters)
    )
    await cb.answer()


# ═══ LEVEL 3: Chapter list for Class 12 ═══
@router.callback_query(F.data.startswith("st12:section:"))
async def st12_section(cb: CallbackQuery):
    section = cb.data.split(":")[2]
    chapters = await get_study_chapters("12", section)
    if not chapters:
        return await cb.answer("ησ ϻᴧᴛєʀiᴧʟ ʏєᴛ.", show_alert=True)
    CHAPTER_CACHE[cb.from_user.id] = chapters
    await cb.message.edit_text(
        f"📕 <b>ᴄʟᴀꜱꜱ 12 — {section.upper()}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\nᴄʜᴏᴏꜱᴇ ᴄʜᴀᴘᴛᴇʀ:",
        reply_markup=chapters_kb("12", section, chapters)
    )
    await cb.answer()


# ═══ LEVEL 4: File list (after chapter clicked) ═══
@router.callback_query(F.data.startswith("stch:"))
async def st_chapter(cb: CallbackQuery):
    parts = cb.data.split(":")
    class_name = parts[1]
    section = parts[2]
    idx = int(parts[3])

    chapters = CHAPTER_CACHE.get(cb.from_user.id, [])
    if idx >= len(chapters):
        return await cb.answer("ᴄнᴧᴩᴛєʀ ησт ғσᴜηᴅ.", show_alert=True)
    chapter = chapters[idx]

    materials = await get_study_materials(class_name, section, chapter)
    if not materials:
        return await cb.answer("ησ ғiʟєs ʏєᴛ.", show_alert=True)

    # Build back target = chapters view of the same section
    if class_name == "10":
        if section == "pyq":
            back_target = f"st10:section:{section}"
        else:
            back_target = f"st10:subject:{section}"
    else:
        back_target = f"st{class_name}:section:{section}"

    await cb.message.edit_text(
        f"📄 <b>{chapter}</b> — {len(materials)} ғɪʟᴇ(ꜱ)",
        reply_markup=back_kb(back_target)
    )

    for m in materials:
        content_type = m["content_type"]
        content = m["content"]
        caption = m["caption"]
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
