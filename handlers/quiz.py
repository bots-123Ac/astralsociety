from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from keyboards.quiz_kb import quiz_menu_kb, quiz_question_kb, quiz_after_kb
from keyboards.main_menu import back_kb
from utils.database import (
    get_random_question, save_quiz_attempt, add_points, add_coins,
)
from utils.ui import smart_edit

router = Router()


async def show_question(cb_or_msg, state: FSMContext, user_id: int):
    data = await state.get_data()
    exam = data.get("exam")
    subject = data.get("subject")
    question = await get_random_question(
        None if exam in (None, "any") else exam,
        subject,
        None,
    )
    if not question:
        text = "📭 <b>ησ ǫᴜєsᴛiσηs ʏєᴛ</b>\n\nᴀᴅᴍɪɴs sᴇ ǫᴜᴇsᴛɪᴏɴs ᴀᴅᴅ ᴋᴀʀᴇɪɴ."
        if hasattr(cb_or_msg, "message"):
            await smart_edit(cb_or_msg, text, back_kb())
        else:
            await cb_or_msg.answer(text)
        return

    qid, ex, sub, top, qtext, a, b, c, d, correct = question
    await state.update_data(
        current_qid=qid, current_correct=correct,
        current_exam=ex, current_subject=sub, current_topic=top,
    )
    text = (
        f"📝 <b>ǫᴜɪᴢ</b> — {ex.upper() if ex else 'ANY'}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>{qtext}</b>\n\n"
        f"ᴄʜᴏᴏsᴇ ᴀɴ ᴀɴsᴡᴇʀ:"
    )
    options = [("A", a), ("B", b), ("C", c), ("D", d)]
    kb = quiz_question_kb(qid, options)
    if hasattr(cb_or_msg, "message"):
        await smart_edit(cb_or_msg, text, kb)
    else:
        await cb_or_msg.answer(text, reply_markup=kb)


@router.message(Command("quiz"))
async def cmd_quiz(message: Message, state: FSMContext):
    await state.clear()
    text = "📝 <b>ǫᴜɪᴢ</b>\n━━━━━━━━━━━━━━━━━━━━━\n\nᴄʜᴏᴏsᴇ ᴇxᴀᴍ:"
    await message.answer(text, reply_markup=quiz_menu_kb())


@router.callback_query(F.data == "menu:quiz")
async def menu_quiz(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    text = "📝 <b>ǫᴜɪᴢ</b>\n━━━━━━━━━━━━━━━━━━━━━\n\nᴄʜᴏᴏsᴇ ᴇxᴀᴍ:"
    await smart_edit(cb, text, quiz_menu_kb())
    await cb.answer()


@router.callback_query(F.data.startswith("qz:start:"))
async def qz_start(cb: CallbackQuery, state: FSMContext):
    exam = cb.data.split(":")[2]
    await state.update_data(exam=exam, subject=None)
    await show_question(cb, state, cb.from_user.id)
    await cb.answer()


@router.callback_query(F.data.startswith("qz:ans:"))
async def qz_answer(cb: CallbackQuery, state: FSMContext):
    parts = cb.data.split(":")
    qid = int(parts[2])
    selected = parts[3]
    data = await state.get_data()
    correct = data.get("current_correct")
    if not correct:
        await cb.answer("sᴇssɪᴏɴ ᴇxᴘɪʀᴇᴅ", show_alert=True)
        return

    is_correct = (selected == correct)
    await save_quiz_attempt(
        cb.from_user.id, qid, selected, 1 if is_correct else 0,
        data.get("current_exam"), data.get("current_subject"), data.get("current_topic")
    )

    if is_correct:
        await add_points(cb.from_user.id, 5)
        await add_coins(cb.from_user.id, 10)
        result = "✅ <b>ᴄᴏʀʀᴇᴄᴛ!</b>\n+5 ᴘᴏɪɴᴛs, +10 ᴄᴏɪɴs"
    else:
        result = f"❌ <b>ᴡʀᴏɴɢ.</b>\nᴄᴏʀʀᴇᴄᴛ ᴀɴsᴡᴇʀ: <b>{correct}</b>"

    text = f"📝 ǫᴜɪᴢ ʀᴇsᴜʟᴛ\n━━━━━━━━━━━━━━━━━━━━━\n\n{result}\n\nᴡʜᴀᴛ ɴᴇxᴛ?"
    await smart_edit(cb, text, quiz_after_kb())
    await cb.answer("✅" if is_correct else "❌")


@router.callback_query(F.data == "qz:next")
async def qz_next(cb: CallbackQuery, state: FSMContext):
    await show_question(cb, state, cb.from_user.id)
    await cb.answer()


@router.callback_query(F.data == "qz:skip")
async def qz_skip(cb: CallbackQuery, state: FSMContext):
    await show_question(cb, state, cb.from_user.id)
    await cb.answer()


@router.callback_query(F.data == "qz:end")
async def qz_end(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await smart_edit(cb, "📝 ǫᴜɪᴢ ᴇɴᴅᴇᴅ. ᴛʜᴀɴᴋs ғᴏʀ ᴘʟᴀʏɪɴɢ!", back_kb())
    await cb.answer()
