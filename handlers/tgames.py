import random
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from config import QUIZ_REWARD_COINS, NUMBER_REWARD_COINS
from keyboards.main_menu import (
    tgames_menu_kb, quiz_menu_kb, quiz_options_kb, quiz_count_kb, back_main_kb,
)
from utils.database import (
    add_coins, add_xp, inc_quiz_attempt, inc_quiz_solved,
    inc_number_attempt, inc_number_guess, has_xp_boost, mission_quiz_done,
    get_random_quiz_question, get_quiz_count,
)

router = Router()

QUIZ_CACHE = {}     # (chat_id, user_id) -> quiz session
NUMBER_CACHE = {}   # (chat_id, user_id) -> personal game

NUMBER_MIN = 100
NUMBER_MAX = 500
NUMBER_MAX_ATTEMPTS = 12

CATEGORY_NAMES = {
    "space": "🚀 ꜱᴘᴀᴄᴇ", "general": "🌍 ɢᴇɴᴇʀᴀʟ",
    "science": "🔬 ꜱᴄɪᴇɴᴄᴇ", "history": "📜 ʜɪꜱᴛᴏʀʏ",
    "geography": "🗺️ ɢᴇᴏɢʀᴀᴘʜʏ", "maths": "🔢 ᴍᴀᴛʜꜱ",
    "tech": "💻 ᴛᴇᴄʜ", "sports": "⚽ ꜱᴘᴏʀᴛꜱ",
    "movies": "🎬 ᴍᴏᴠɪᴇꜱ", "music": "🎵 ᴍᴜꜱɪᴄ",
    "animals": "🐾 ᴀɴɪᴍᴀʟꜱ", "food": "🍔 ꜰᴏᴏᴅ",
    "literature": "📖 ʟɪᴛᴇʀᴀᴛᴜʀᴇ", "politics": "🏛️ ᴘᴏʟɪᴛɪᴄꜱ",
    "business": "💰 ʙᴜꜱɪɴᴇꜱꜱ",
}


# ═══════════════════════════════════════════════
# /tgames entry
# ═══════════════════════════════════════════════
@router.message(F.text.regexp(r"^/tgames(\s|$)"))
async def cmd_tgames(message: Message):
    await message.answer(
        "🎮 <b>ᴀꜱᴛʀᴀʟ ᴛ-ɢᴀᴍᴇꜱ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\nᴄʜᴏᴏꜱᴇ ᴀ ɢᴀᴍᴇ:",
        reply_markup=tgames_menu_kb()
    )


# ═══════════════════════════════════════════════
# QUIZ
# ═══════════════════════════════════════════════
@router.callback_query(F.data == "tg:quiz")
async def quiz_select(cb: CallbackQuery):
    total = await get_quiz_count()
    await cb.message.edit_text(
        f"🧠 <b>ǫᴜɪᴢ</b>\n<i>ᴛᴏᴛᴀʟ: {total:,} ǫᴜᴇꜱᴛɪᴏɴꜱ</i>\n\nʜᴏᴡ ᴍᴀɴʏ ǫᴜᴇꜱᴛɪᴏɴꜱ?",
        reply_markup=quiz_count_kb()
    )
    await cb.answer()


@router.callback_query(F.data.startswith("qzcount:"))
async def quiz_count_selected(cb: CallbackQuery):
    count = int(cb.data.split(":")[1])
    QUIZ_CACHE[(cb.message.chat.id, cb.from_user.id)] = {
        "total": count, "done": 0, "score": 0, "correct": 0, "wrong": 0,
        "used_ids": set(),
    }
    await cb.message.edit_text(
        f"🧠 <b>ǫᴜɪᴢ — {count} ǫᴜᴇꜱᴛɪᴏɴꜱ</b>\n\nᴄʜᴏᴏꜱᴇ ᴄᴀᴛᴇɢᴏʀʏ:",
        reply_markup=quiz_menu_kb()
    )
    await cb.answer()


@router.callback_query(F.data.startswith("quiz:"))
async def quiz_start(cb: CallbackQuery):
    cat = cb.data.split(":")[1]
    if cat not in CATEGORY_NAMES:
        return await cb.answer()
    key = (cb.message.chat.id, cb.from_user.id)
    sess = QUIZ_CACHE.get(key)
    if not sess:
        sess = {"total": 5, "done": 0, "score": 0, "correct": 0, "wrong": 0, "used_ids": set()}
        QUIZ_CACHE[key] = sess
    sess["category"] = cat
    await _send_quiz_question(cb, cat, key)


async def _send_quiz_question(cb: CallbackQuery, cat: str, key: tuple):
    sess = QUIZ_CACHE.get(key)
    if not sess:
        return await cb.answer("ꜱᴇꜱꜱɪᴏɴ ᴇxᴘɪʀᴇᴅ.", show_alert=True)
    if sess["done"] >= sess["total"]:
        return await _finish_quiz(cb, key)

    q = None
    for _ in range(10):
        row = await get_random_quiz_question(cat)
        if not row:
            break
        if row[0] not in sess["used_ids"]:
            q = row
            break
    if not q:
        row = await get_random_quiz_question(cat)
        if not row:
            return await cb.answer("ɴᴏ ǫᴜᴇꜱᴛɪᴏɴꜱ.", show_alert=True)
        q = row

    qid, question, a, b, c, d, correct = q
    sess["used_ids"].add(qid)
    sess["current"] = (qid, correct, question, a, b, c, d)

    cat_label = CATEGORY_NAMES.get(cat, cat.upper())
    await cb.message.edit_text(
        f"🧠 <b>{cat_label}</b>\n"
        f"ǫ: <b>{sess['done'] + 1}/{sess['total']}</b>  |  ꜱᴄᴏʀᴇ: <b>{sess['score']}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n<b>{question}</b>\n\nᴄʜᴏᴏꜱᴇ:",
        reply_markup=quiz_options_kb(qid, a, b, c, d)
    )
    await cb.answer()


@router.callback_query(F.data.startswith("qans:"))
async def quiz_answer(cb: CallbackQuery):
    parts = cb.data.split(":")
    qid, selected = int(parts[1]), parts[2]
    key = (cb.message.chat.id, cb.from_user.id)
    sess = QUIZ_CACHE.get(key)
    if not sess or "current" not in sess or sess["current"][0] != qid:
        return await cb.answer("ꜱᴇꜱꜱɪᴏɴ ᴇxᴘɪʀᴇᴅ.", show_alert=True)

    _, correct, *_ = sess["current"]
    is_correct = (selected == correct)

    await inc_quiz_attempt(cb.from_user.id)
    if is_correct:
        sess["score"] += 2
        sess["correct"] += 1
        await inc_quiz_solved(cb.from_user.id)
        try:
            await mission_quiz_done(cb.from_user.id, 1)
        except Exception:
            pass
    else:
        sess["wrong"] += 1
        if sess["wrong"] % 2 == 0:
            sess["score"] -= 1

    sess["done"] += 1
    if sess["done"] >= sess["total"]:
        return await _finish_quiz(cb, key)
    await _send_quiz_question(cb, sess.get("category"), key)


async def _finish_quiz(cb: CallbackQuery, key: tuple):
    sess = QUIZ_CACHE.pop(key, None)
    if not sess:
        return await cb.answer("ꜱᴇꜱꜱɪᴏɴ ᴇxᴘɪʀᴇᴅ.", show_alert=True)

    correct = sess["correct"]
    wrong = sess["wrong"]
    score = sess["score"]

    coins = max(0, correct * QUIZ_REWARD_COINS)
    xp = random.randint(0, 5) * correct
    if await has_xp_boost(cb.from_user.id):
        xp *= 2

    if coins > 0:
        await add_coins(cb.from_user.id, coins)
    if xp > 0:
        await add_xp(cb.from_user.id, xp)

    await cb.message.edit_text(
        f"🏁 <b>ǫᴜɪᴢ ᴄᴏᴍᴘʟᴇᴛᴇᴅ!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📝 ᴛᴏᴛᴀʟ: <b>{sess['total']}</b>\n"
        f"✅ ᴄᴏʀʀᴇᴄᴛ: <b>{correct}</b>\n"
        f"❌ ᴡʀᴏɴɢ: <b>{wrong}</b>\n"
        f"🎯 ꜰɪɴᴀʟ ꜱᴄᴏʀᴇ: <b>{score}</b>\n\n"
        f"🪙 +{coins} ᴄᴏɪɴꜱ\n📈 +{xp} xᴘ",
        reply_markup=back_main_kb()
    )
    await cb.answer("🏁")


# ═══════════════════════════════════════════════
# PERSONAL NUMBER GAME — /tgames → Number
# ═══════════════════════════════════════════════
@router.callback_query(F.data == "tg:number")
async def number_start(cb: CallbackQuery):
    secret = random.randint(NUMBER_MIN, NUMBER_MAX)
    key = (cb.message.chat.id, cb.from_user.id)
    NUMBER_CACHE[key] = {
        "secret": secret,
        "attempts": 0,
        "low": NUMBER_MIN,
        "high": NUMBER_MAX,
    }
    await inc_number_attempt(cb.from_user.id)
    await cb.message.edit_text(
        "🔢 <b>ɢᴜᴇꜱꜱ ᴛʜᴇ ɴᴜᴍʙᴇʀ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 ʀᴀɴɢᴇ: <b>{NUMBER_MIN}–{NUMBER_MAX}</b>\n"
        f"🎲 ᴍᴀx ᴄʜᴀɴᴄᴇꜱ: <b>{NUMBER_MAX_ATTEMPTS}</b>\n\n"
        "ᴜꜱᴇ <code>/h &lt;ɴᴜᴍʙᴇʀ&gt;</code> ᴛᴏ ɢᴜᴇꜱꜱ.\n"
        "ᴇxᴀᴍᴘʟᴇ: <code>/h 250</code>"
    )
    await cb.answer()


# ═══════════════════════════════════════════════
# /h — WORKS EVERYWHERE (DM + GC + Group)
# Priority: Event (if GC has active event) → Personal Game
# ═══════════════════════════════════════════════
@router.message(F.text.regexp(r"^/h(\s|$)"))
async def number_guess(message: Message):
    # 1️⃣ Try event first (only in groups)
    try:
        from handlers.events import try_handle_event_guess
        handled = await try_handle_event_guess(message)
        if handled:
            return
    except Exception as e:
        import logging
        logging.error(f"event guess err: {e}")

    # 2️⃣ Personal game — auto-start if none exists
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip().isdigit():
        return await message.reply("ᴜꜱᴀɢᴇ: <code>/h 250</code>")

    user_id = message.from_user.id
    key = (message.chat.id, user_id)
    game = NUMBER_CACHE.get(key)

    # Auto-start if not started
    if not game:
        secret = random.randint(NUMBER_MIN, NUMBER_MAX)
        game = {
            "secret": secret,
            "attempts": 0,
            "low": NUMBER_MIN,
            "high": NUMBER_MAX,
        }
        NUMBER_CACHE[key] = game
        await inc_number_attempt(user_id)

    guess = int(parts[1].strip())
    if not (NUMBER_MIN <= guess <= NUMBER_MAX):
        return await message.reply(
            f"❌ ɢᴜᴇꜱꜱ ʙᴇᴛᴡᴇᴇɴ {NUMBER_MIN} ᴀɴᴅ {NUMBER_MAX}."
        )

    game["attempts"] += 1
    await inc_number_guess(user_id)
    secret = game["secret"]

    # ═══ CORRECT ═══
    if guess == secret:
        coins = NUMBER_REWARD_COINS
        xp_gain = random.randint(0, 12)
        if await has_xp_boost(user_id):
            xp_gain *= 2
        await add_coins(user_id, coins)
        await add_xp(user_id, xp_gain)
        NUMBER_CACHE.pop(key, None)
        return await message.reply(
            f"🎉 <b>ᴄᴏʀʀᴇᴄᴛ!</b>\n\n"
            f"ꜱᴇᴄʀᴇᴛ: <b>{secret}</b>\nᴀᴛᴛᴇᴍᴘᴛꜱ: <b>{game['attempts']}</b>\n\n"
            f"🪙 +{coins} | 📈 +{xp_gain} xᴘ"
        )

    remaining = NUMBER_MAX_ATTEMPTS - game["attempts"]

    # ═══ GAME OVER ═══
    if game["attempts"] >= NUMBER_MAX_ATTEMPTS:
        NUMBER_CACHE.pop(key, None)
        return await message.reply(
            f"💀 <b>ɢᴀᴍᴇ ᴏᴠᴇʀ!</b>\n\nꜱᴇᴄʀᴇᴛ ᴡᴀꜱ <b>{secret}</b>"
        )

    # ═══ FEEDBACK ═══
    if guess > secret:
        game["high"] = min(game["high"], guess - 1)
        arrow, label = "📈", "ᴛᴏᴏ ʜɪɢʜ"
    else:
        game["low"] = max(game["low"], guess + 1)
        arrow, label = "📉", "ᴛᴏᴏ ʟᴏᴡ"

    await message.reply(
        f"{arrow} [ <b>{guess}</b> ] ɪꜱ {label}!\n"
        f"🎯 ʀᴀɴɢᴇ: [ <b>{game['low']} ──── {game['high']}</b> ]\n"
        f"⚠️ ᴀᴛᴛᴇᴍᴘᴛꜱ ʟᴇꜰᴛ: <b>{remaining}</b>"
    )
