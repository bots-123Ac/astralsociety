from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.study_kb import (
    study_main_kb, education_kb, class_kb, category_kb, subject_kb,
    chapters_kb, RESOURCE_TYPE_LABELS,
)
from keyboards.main_menu import back_kb
from utils.database import get_chapters, get_resources
from utils.ui import smart_edit

router = Router()


class StudyBrowse(StatesGroup):
    active = State()


@router.callback_query(F.data == "menu:study")
async def show_study(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    text = (
        "📚 <b>sᴛᴜᴅʏ sєᴄᴛiση</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "ᴡнᴧᴛ ᴅσ ʏσᴜ ᴡᴧηηᴧ sᴛᴜᴅʏ тσᴅᴧʏ?"
    )
    await smart_edit(cb, text, study_main_kb())
    await cb.answer()


@router.callback_query(F.data.startswith("study:rt:"))
async def choose_rt(cb: CallbackQuery, state: FSMContext):
    rt = cb.data.split(":")[2]
    await state.set_state(StudyBrowse.active)
    await state.update_data(rt=rt)
    label = RESOURCE_TYPE_LABELS.get(rt, rt)
    text = f"{label}\n━━━━━━━━━━━━━━━━━━━━━\n\nsєʟєᴄᴛ єᴅᴜᴄᴧᴛiση тʏᴩє:"
    await smart_edit(cb, text, education_kb())
    await cb.answer()


@router.callback_query(F.data.startswith("study:edu:"))
async def choose_edu(cb: CallbackQuery, state: FSMContext):
    edu = cb.data.split(":")[2]
    await state.update_data(edu=edu)
    if edu in ("jee", "neet"):
        await state.update_data(cls="na")
        text = "🔬 sєʟєᴄᴛ ᴄᴧᴛєɢσʀʏ:"
        await smart_edit(cb, text, category_kb())
    else:
        text = "🏫 sєʟєᴄᴛ ᴄʟᴧss:"
        await smart_edit(cb, text, class_kb())
    await cb.answer()


@router.callback_query(F.data.startswith("study:cls:"))
async def choose_cls(cb: CallbackQuery, state: FSMContext):
    cls = cb.data.split(":")[2]
    await state.update_data(cls=cls)
    text = "🔬 sєʟєᴄᴛ ᴄᴧᴛєɢσʀʏ:"
    await smart_edit(cb, text, category_kb())
    await cb.answer()


@router.callback_query(F.data.startswith("study:cat:"))
async def choose_cat(cb: CallbackQuery, state: FSMContext):
    cat = cb.data.split(":")[2]
    await state.update_data(cat=cat)
    text = "📚 sєʟєᴄᴛ sᴜвᴊєᴄᴛ:"
    await smart_edit(cb, text, subject_kb(cat))
    await cb.answer()


@router.callback_query(F.data.startswith("study:sub:"))
async def choose_sub(cb: CallbackQuery, state: FSMContext):
    sub = cb.data.split(":", 2)[2]
    await state.update_data(sub=sub)
    data = await state.get_data()

    chapters = await get_chapters(
        data["edu"], data["cls"], data["cat"], sub, data["rt"]
    )
    await state.update_data(chapter_list=[ch for ch, _ in chapters])

    if not chapters:
        text = (
            f"📭 <b>ησ ʀєsσᴜʀᴄєs ʏєᴛ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"sᴜвᴊєᴄᴛ: <b>{sub}</b>\n"
            f"ᴛʏᴩє: {RESOURCE_TYPE_LABELS.get(data['rt'], data['rt'])}\n\n"
            f"ᴧᴅϻiηs sє ϻᴧᴛєʀiᴧʟ ᴜᴩʟσᴧᴅ ηнi нᴜᴧ."
        )
        await smart_edit(cb, text, back_kb("menu:study"))
    else:
        text = (
            f"📖 <b>{sub}</b> — ᴄнᴧᴩᴛєʀs\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"ᴄнσσsє ᴧ ᴄнᴧᴩᴛєʀ:"
        )
        await smart_edit(cb, text, chapters_kb(chapters))
    await cb.answer()


@router.callback_query(F.data.startswith("study:chp:"))
async def show_chapter(cb: CallbackQuery, state: FSMContext):
    idx = int(cb.data.split(":")[2])
    data = await state.get_data()
    if not data.get("edu") or not data.get("chapter_list"):
        await cb.answer("sєssiση єxᴩiʀєᴅ. sᴛᴧʀᴛ ᴧɢᴧiη.", show_alert=True)
        return

    try:
        chapter = data["chapter_list"][idx]
    except IndexError:
        await cb.answer("ᴄнᴧᴩᴛєʀ ησᴛ ғσᴜηᴅ.", show_alert=True)
        return

    files = await get_resources(
        data["edu"], data["cls"], data["cat"], data["sub"], chapter, data["rt"]
    )

    await smart_edit(
        cb,
        f"📁 <b>{chapter}</b> — {len(files)} ʀєsσᴜʀᴄє(s)",
        back_kb("menu:study"),
    )

    for content_type, content, caption in files:
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
            try:
                await cb.message.answer(f"📄 {caption or 'Resource'}\n{content}")
            except Exception:
                pass
    await cb.answer()


# ─── Back navigation ───

@router.callback_query(F.data == "study:back:edu")
async def back_edu(cb: CallbackQuery):
    await smart_edit(cb, "sєʟєᴄᴛ єᴅᴜᴄᴧᴛiση тʏᴩє:", education_kb())
    await cb.answer()


@router.callback_query(F.data == "study:back:cls")
async def back_cls(cb: CallbackQuery):
    await smart_edit(cb, "sєʟєᴄᴛ ᴄʟᴧss:", class_kb())
    await cb.answer()


@router.callback_query(F.data == "study:back:cat")
async def back_cat(cb: CallbackQuery):
    await smart_edit(cb, "sєʟєᴄᴛ ᴄᴧᴛєɢσʀʏ:", category_kb())
    await cb.answer()


@router.callback_query(F.data == "study:back:sub")
async def back_sub(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cat = data.get("cat", "general")
    await smart_edit(cb, "sєʟєᴄᴛ sᴜвᴊєᴄᴛ:", subject_kb(cat))
    await cb.answer()
