from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.study_kb import (
    boards_kb, classes_kb, subjects_kb, chapters_kb, materials_kb,
    SUBJECTS_BY_BOARD,
)
from keyboards.main_menu import back_kb
from utils.database import (
    get_subjects, get_chapters, get_material_types, get_resources,
)
from utils.ui import smart_edit

router = Router()


@router.callback_query(F.data == "menu:study")
async def study_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    text = (
        "📚 <b>sᴛᴜᴅʏ ϻᴧᴛєʀiᴧʟ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "ᴄнσσsє ᴛнє ʙᴏᴀʀᴅ:"
    )
    await smart_edit(cb, text, boards_kb())
    await cb.answer()


@router.callback_query(F.data.startswith("study:board:"))
async def study_board(cb: CallbackQuery, state: FSMContext):
    board = cb.data.split(":")[2]
    await state.update_data(board=board)
    if board in ("jee", "neet"):
        # Skip class — no class for JEE/NEET
        await state.update_data(cls="na")
        subjects = SUBJECTS_BY_BOARD.get(board, [])
        # Merge with DB subjects
        db_subs = await get_subjects(board, "na")
        all_subs = list(set(subjects + db_subs))
        text = f"📚 sєʟєᴄᴛ sᴜʙᴊєᴄᴛ ({board.upper()}):"
        await smart_edit(cb, text, subjects_kb(board, "na", all_subs))
    else:
        text = "🏫 sєʟєᴄᴛ ᴄʟᴧss:"
        await smart_edit(cb, text, classes_kb())
    await cb.answer()


@router.callback_query(F.data.startswith("study:cls:"))
async def study_cls(cb: CallbackQuery, state: FSMContext):
    cls = cb.data.split(":")[2]
    await state.update_data(cls=cls)
    data = await state.get_data()
    board = data.get("board")
    key = f"{board}_{cls}"
    default_subs = SUBJECTS_BY_BOARD.get(key, [])
    db_subs = await get_subjects(board, cls)
    all_subs = list(set(default_subs + db_subs))
    text = f"📚 sєʟєᴄᴛ sᴜʙᴊєᴄᴛ (ᴄʟᴧss {cls}):"
    await smart_edit(cb, text, subjects_kb(board, cls, all_subs))
    await cb.answer()


@router.callback_query(F.data.startswith("study:sub:"))
async def study_sub(cb: CallbackQuery, state: FSMContext):
    sub = cb.data.split(":", 2)[2]
    await state.update_data(sub=sub)
    data = await state.get_data()
    chapters = await get_chapters(data["board"], data["cls"], sub)
    await state.update_data(chapters=[c for c, _ in chapters])

    if not chapters:
        text = (
            f"📭 <b>ησ ᴍᴀᴛᴇʀɪᴀʟ ʏᴇᴛ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"sᴜʙᴊᴇᴄᴛ: <b>{sub}</b>\n\n"
            f"ᴀᴅᴍɪɴs sᴇ ᴍᴀᴛᴇʀɪᴀʟ ᴜᴘʟᴏᴀᴅ ɴʜɪ ʜᴜᴀ ʜᴀɪ."
        )
        await smart_edit(cb, text, back_kb("menu:study"))
    else:
        text = f"📖 <b>{sub}</b> — ᴄнᴧᴩᴛєʀs:"
        await smart_edit(cb, text, chapters_kb(chapters))
    await cb.answer()


@router.callback_query(F.data.startswith("study:chp:"))
async def study_chp(cb: CallbackQuery, state: FSMContext):
    idx = int(cb.data.split(":")[2])
    data = await state.get_data()
    chapters = data.get("chapters", [])
    if idx >= len(chapters):
        await cb.answer("ᴇxᴘɪʀᴇᴅ", show_alert=True)
        return
    chapter = chapters[idx]
    await state.update_data(chapter=chapter, chapter_idx=idx)
    materials = await get_material_types(data["board"], data["cls"], data["sub"], chapter)
    if not materials:
        await cb.answer("ησ ϻᴧᴛєʀiᴧʟ", show_alert=True)
        return
    text = f"📄 <b>{chapter}</b> — sєʟєᴄᴛ тʏᴩє:"
    await smart_edit(cb, text, materials_kb(materials))
    await cb.answer()


@router.callback_query(F.data.startswith("study:mat:"))
async def study_mat(cb: CallbackQuery, state: FSMContext):
    mtype = cb.data.split(":")[2]
    data = await state.get_data()
    files = await get_resources(
        data["board"], data["cls"], data["sub"], data["chapter"], mtype
    )
    if not files:
        await cb.answer("ησ ϻᴧᴛєʀiᴧʟ", show_alert=True)
        return

    await smart_edit(
        cb,
        f"📁 <b>{data['chapter']}</b> — {len(files)} ғɪʟᴇ(s)",
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


# Back navigation
@router.callback_query(F.data == "study:back:cls")
async def back_cls(cb: CallbackQuery):
    await smart_edit(cb, "🏫 sєʟєᴄᴛ ᴄʟᴧss:", classes_kb())
    await cb.answer()


@router.callback_query(F.data == "study:back:sub")
async def back_sub(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    board = data.get("board")
    cls = data.get("cls")
    key = f"{board}_{cls}"
    default_subs = SUBJECTS_BY_BOARD.get(key, SUBJECTS_BY_BOARD.get(board, []))
    db_subs = await get_subjects(board, cls)
    all_subs = list(set(default_subs + db_subs))
    await smart_edit(cb, "📚 sєʟєᴄᴛ sᴜʙᴊєᴄᴛ:", subjects_kb(board, cls, all_subs))
    await cb.answer()


@router.callback_query(F.data == "study:back:chp")
async def back_chp(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    chapters = data.get("chapters", [])
    chapter_data = [(ch, 0) for ch in chapters]
    await smart_edit(cb, "📖 ᴄнᴧᴩᴛєʀs:", chapters_kb(chapter_data))
    await cb.answer()
