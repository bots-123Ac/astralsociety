import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.admin_kb import (
    admin_panel_kb, adm_boards_kb, adm_classes_kb, adm_subjects_kb,
    adm_material_type_kb, adm_confirm_kb, adm_quiz_exam_kb, adm_quiz_confirm_kb,
)
from keyboards.main_menu import back_kb
from keyboards.study_kb import SUBJECTS_BY_BOARD
from utils.permissions import is_admin
from utils.database import save_resource, add_quiz_question, get_study_stats
from utils.ui import smart_edit

router = Router()
logger = logging.getLogger(__name__)


class AdmStudy(StatesGroup):
    chapter = State()
    content = State()


class AdmQuiz(StatesGroup):
    subject = State()
    topic = State()
    question = State()
    a = State()
    b = State()
    c = State()
    d = State()
    correct = State()


def parse_content(message: Message):
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
        return ("link", message.text.strip(), caption)
    return (None, None, None)


# ─── ENTRY ───
@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("❌ sσηʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
        return
    await state.clear()
    text = "👑 <b>ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ</b>\n━━━━━━━━━━━━━━━━━━━━━\n\nᴄʜᴏᴏsᴇ ᴀɴ ᴀᴄᴛɪᴏɴ:"
    await message.answer(text, reply_markup=admin_panel_kb())


@router.callback_query(F.data == "adm:stats")
async def adm_stats(cb: CallbackQuery):
    if not is_admin(cb.from_user.id):
        await cb.answer("❌", show_alert=True); return
    total = await get_study_stats()
    text = f"📊 <b>sᴛᴀᴛs</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n📚 sᴛᴜᴅʏ ʀᴇsᴏᴜʀᴄᴇs: <b>{total}</b>"
    await smart_edit(cb, text, admin_panel_kb())
    await cb.answer()


@router.callback_query(F.data == "adm:cancel")
async def adm_cancel(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await smart_edit(cb, "❌ ᴄᴀɴᴄᴇʟʟᴇᴅ.", admin_panel_kb())
    await cb.answer()


# ─── ADD STUDY MATERIAL ───
@router.callback_query(F.data == "adm:add:study")
async def adm_add_study(cb: CallbackQuery, state: FSMContext):
    if not is_admin(cb.from_user.id):
        await cb.answer("❌", show_alert=True); return
    await state.clear()
    await state.update_data(pending=[])
    text = "📤 <b>ᴀᴅᴅ sᴛᴜᴅʏ ᴍᴀᴛᴇʀɪᴀʟ</b>\n━━━━━━━━━━━━━━━━━━━━━\n\nsᴇʟᴇᴄᴛ ʙᴏᴀʀᴅ:"
    await smart_edit(cb, text, adm_boards_kb())
    await cb.answer()


@router.callback_query(F.data.startswith("adm:board:"))
async def adm_board(cb: CallbackQuery, state: FSMContext):
    board = cb.data.split(":")[2]
    await state.update_data(board=board)
    if board in ("jee", "neet"):
        await state.update_data(cls="na")
        subs = SUBJECTS_BY_BOARD.get(board, [])
        await smart_edit(cb, "📚 sᴇʟᴇᴄᴛ sᴜʙᴊᴇᴄᴛ:", adm_subjects_kb(subs))
    else:
        await smart_edit(cb, "🏫 sᴇʟᴇᴄᴛ ᴄʟᴀss:", adm_classes_kb())
    await cb.answer()


@router.callback_query(F.data.startswith("adm:cls:"))
async def adm_cls(cb: CallbackQuery, state: FSMContext):
    cls = cb.data.split(":")[2]
    await state.update_data(cls=cls)
    data = await state.get_data()
    subs = SUBJECTS_BY_BOARD.get(f"{data['board']}_{cls}", [])
    await smart_edit(cb, "📚 sᴇʟᴇᴄᴛ sᴜʙᴊᴇᴄᴛ:", adm_subjects_kb(subs))
    await cb.answer()


@router.callback_query(F.data.startswith("adm:sub:"))
async def adm_sub(cb: CallbackQuery, state: FSMContext):
    sub = cb.data.split(":", 2)[2]
    await state.update_data(sub=sub)
    await state.set_state(AdmStudy.chapter)
    text = f"📚 sᴜʙᴊᴇᴄᴛ: <b>{sub}</b>\n\nsᴇɴᴅ ᴛʜᴇ ᴄʜᴀᴘᴛᴇʀ ɴᴀᴍᴇ (ᴛᴇxᴛ):"
    await smart_edit(cb, text, back_kb("adm:cancel"))
    await cb.answer()


@router.message(AdmStudy.chapter)
async def adm_chapter(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    chapter = message.text.strip()
    await state.update_data(chapter=chapter)
    text = f"ᴄʜᴀᴘᴛᴇʀ: <b>{chapter}</b>\n\nᴡʜᴀᴛ ᴛʏᴘᴇ ᴏғ ᴍᴀᴛᴇʀɪᴀʟ?"
    await message.answer(text, reply_markup=adm_material_type_kb())


@router.callback_query(F.data.startswith("adm:mt:"))
async def adm_mt(cb: CallbackQuery, state: FSMContext):
    mt = cb.data.split(":")[2]
    await state.update_data(current_mt=mt)
    await state.set_state(AdmStudy.content)
    text = (
        f"📤 <b>sᴇɴᴅ ᴛʜᴇ {mt.upper()}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"sᴇɴᴅ ᴀ ʟɪɴᴋ, PDF, ᴠɪᴅᴇᴏ, ɪᴍᴀɢᴇ ᴏʀ ᴅᴏᴄᴜᴍᴇɴᴛ."
    )
    await smart_edit(cb, text, back_kb("adm:cancel"))
    await cb.answer()


@router.message(AdmStudy.content)
async def adm_content(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    ct, content, caption = parse_content(message)
    if not content:
        await message.answer("❌ sᴇɴᴅ ᴀ ʟɪɴᴋ ᴏʀ ғɪʟᴇ.")
        return
    data = await state.get_data()
    mt = data.get("current_mt")
    pending = data.get("pending", [])
    pending.append({
        "material_type": mt, "content_type": ct,
        "content": content, "caption": caption,
    })
    await state.update_data(pending=pending)
    text = (
        f"✅ ᴀᴅᴅᴇᴅ: <b>{mt}</b>\n"
        f"sᴏ ғᴀʀ: <b>{len(pending)}</b> ɪᴛᴇᴍ(s)\n\n"
        f"ᴡʜᴀᴛ ɴᴇxᴛ?"
    )
    await message.answer(text, reply_markup=adm_confirm_kb())


@router.callback_query(F.data == "adm:addmore")
async def adm_addmore(cb: CallbackQuery, state: FSMContext):
    await smart_edit(cb, "ᴡʜᴀᴛ ᴛʏᴘᴇ ᴏғ ᴍᴀᴛᴇʀɪᴀʟ?", adm_material_type_kb())
    await cb.answer()


@router.callback_query(F.data == "adm:save")
async def adm_save(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    pending = data.get("pending", [])
    if not pending:
        await cb.answer("ɴᴏ ɪᴛᴇᴍs", show_alert=True); return
    saved = 0
    for item in pending:
        ok = await save_resource(
            data["board"], data["cls"], data["sub"], data["chapter"],
            item["material_type"], item["content_type"],
            item["content"], item["caption"], cb.from_user.id,
        )
        if ok:
            saved += 1
    await state.clear()
    text = (
        f"✅ <b>sᴀᴠᴇᴅ {saved}/{len(pending)} ɪᴛᴇᴍ(s)</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ᴄʜᴀᴘᴛᴇʀ: <b>{data['chapter']}</b>\n"
        f"sᴜʙᴊᴇᴄᴛ: <b>{data['sub']}</b>\n\n"
        f"ᴜsᴇʀs ᴄᴀɴ ɴᴏᴡ sᴇᴇ ᴛʜᴇᴍ ɪɴ sᴛᴜᴅʏ sᴇᴄᴛɪᴏɴ."
    )
    await smart_edit(cb, text, admin_panel_kb())
    await cb.answer()


# ─── ADD QUIZ QUESTION ───
@router.callback_query(F.data == "adm:add:quiz")
async def adm_add_quiz(cb: CallbackQuery, state: FSMContext):
    if not is_admin(cb.from_user.id):
        await cb.answer("❌", show_alert=True); return
    await state.clear()
    text = "📝 <b>ᴀᴅᴅ ǫᴜɪᴢ ǫᴜᴇsᴛɪᴏɴ</b>\n\nsᴇʟᴇᴄᴛ ᴇxᴀᴍ:"
    await smart_edit(cb, text, adm_quiz_exam_kb())
    await cb.answer()


@router.callback_query(F.data.startswith("qz:exam:"))
async def adm_quiz_exam(cb: CallbackQuery, state: FSMContext):
    exam = cb.data.split(":")[2]
    await state.update_data(exam=exam)
    await state.set_state(AdmQuiz.subject)
    await smart_edit(cb, "📚 sᴇɴᴅ sᴜʙᴊᴇᴄᴛ ɴᴀᴍᴇ:", back_kb("adm:cancel"))
    await cb.answer()


@router.message(AdmQuiz.subject)
async def adm_quiz_subject(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.update_data(subject=message.text.strip())
    await state.set_state(AdmQuiz.topic)
    await message.answer("📖 sᴇɴᴅ ᴛᴏᴘɪᴄ ɴᴀᴍᴇ:")


@router.message(AdmQuiz.topic)
async def adm_quiz_topic(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.update_data(topic=message.text.strip())
    await state.set_state(AdmQuiz.question)
    await message.answer("❓ sᴇɴᴅ ᴛʜᴇ ǫᴜᴇsᴛɪᴏɴ ᴛᴇxᴛ:")


@router.message(AdmQuiz.question)
async def adm_quiz_q(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.update_data(question=message.text.strip())
    await state.set_state(AdmQuiz.a)
    await message.answer("🅰️ sᴇɴᴅ ᴏᴘᴛɪᴏɴ A:")


@router.message(AdmQuiz.a)
async def adm_quiz_a(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.update_data(a=message.text.strip())
    await state.set_state(AdmQuiz.b)
    await message.answer("🅱️ sᴇɴᴅ ᴏᴘᴛɪᴏɴ B:")


@router.message(AdmQuiz.b)
async def adm_quiz_b(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.update_data(b=message.text.strip())
    await state.set_state(AdmQuiz.c)
    await message.answer("🇨 sᴇɴᴅ ᴏᴘᴛɪᴏɴ C:")


@router.message(AdmQuiz.c)
async def adm_quiz_c(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.update_data(c=message.text.strip())
    await state.set_state(AdmQuiz.d)
    await message.answer("🇩 sᴇɴᴅ ᴏᴘᴛɪᴏɴ D:")


@router.message(AdmQuiz.d)
async def adm_quiz_d(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.update_data(d=message.text.strip())
    await state.set_state(AdmQuiz.correct)
    await message.answer("✅ sᴇɴᴅ ᴄᴏʀʀᴇᴄᴛ ᴏᴘᴛɪᴏɴ (A/B/C/D):")


@router.message(AdmQuiz.correct)
async def adm_quiz_correct(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    correct = message.text.strip().upper()
    if correct not in ("A", "B", "C", "D"):
        await message.answer("❌ sᴇɴᴅ ᴏɴʟʏ A/B/C/D")
        return
    data = await state.get_data()
    await add_quiz_question(
        data["exam"], data["subject"], data["topic"], data["question"],
        data["a"], data["b"], data["c"], data["d"], correct,
    )
    await state.clear()
    await message.answer(
        f"✅ <b>ǫᴜᴇsᴛɪᴏɴ sᴀᴠᴇᴅ!</b>\n\n"
        f"ᴇxᴀᴍ: {data['exam']}\n"
        f"sᴜʙᴊᴇᴄᴛ: {data['subject']}\n"
        f"ᴛᴏᴘɪᴄ: {data['topic']}\n"
        f"ᴄᴏʀʀᴇᴄᴛ: {correct}",
        reply_markup=admin_panel_kb()
    )
