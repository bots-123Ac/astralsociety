import random
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.event.bases import SkipHandler

from config import QUIZ_REWARD_COINS, NUMBER_REWARD_COINS, WORD_MAX_REWARD
from keyboards.main_menu import (
    tgames_menu_kb, quiz_menu_kb, quiz_options_kb, quiz_count_kb, back_main_kb,
)
from utils.words import get_random_5letter_word, is_valid_word
from utils.database import (
    add_coins, add_xp, inc_quiz_attempt, inc_quiz_solved,
    inc_word_attempt, inc_word_solved, inc_number_attempt, inc_number_guess,
    has_xp_boost, mission_word_played, get_daily_word_attempts,
    inc_daily_word_attempts,
)

router = Router()

# ═══ SESSION CACHES — keyed by (chat_id, user_id) ═══
QUIZ_CACHE = {}
WORD_CACHE = {}
NUMBER_CACHE = {}

DAILY_WORD_LIMIT = 3

QUIZ_SPACE = [
    ("Which planet is known as the Red Planet?", "Venus", "Mars", "Jupiter", "Saturn", "B"),
    ("Largest planet in our solar system?", "Earth", "Saturn", "Jupiter", "Neptune", "C"),
    ("How many moons does Earth have?", "1", "2", "3", "0", "A"),
    ("Which planet has the most moons?", "Jupiter", "Saturn", "Uranus", "Neptune", "B"),
    ("Closest planet to the Sun?", "Venus", "Earth", "Mercury", "Mars", "C"),
    ("Which planet has prominent rings?", "Mars", "Saturn", "Venus", "Mercury", "B"),
    ("What galaxy is Earth in?", "Andromeda", "Milky Way", "Sombrero", "Whirlpool", "B"),
    ("Hottest planet?", "Mercury", "Venus", "Mars", "Jupiter", "B"),
    ("How many planets in solar system?", "7", "8", "9", "10", "B"),
    ("Which planet spins fastest?", "Earth", "Jupiter", "Saturn", "Mars", "B"),
    ("What is the Sun mainly made of?", "Oxygen", "Hydrogen", "Helium", "Carbon", "B"),
    ("Which moon is largest?", "Titan", "Ganymede", "Europa", "Io", "B"),
    ("How far is Sun from Earth (AU)?", "0.5", "1", "2", "5", "B"),
    ("Which planet is coldest?", "Mars", "Jupiter", "Neptune", "Uranus", "C"),
    ("What is a shooting star?", "Star", "Meteor", "Planet", "Comet", "B"),
]

QUIZ_GENERAL = [
    ("Capital of France?", "London", "Paris", "Rome", "Berlin", "B"),
    ("Who wrote Romeo and Juliet?", "Dickens", "Shakespeare", "Tolstoy", "Twain", "B"),
    ("Largest ocean?", "Atlantic", "Indian", "Pacific", "Arctic", "C"),
    ("Which gas do plants absorb?", "Oxygen", "Nitrogen", "CO2", "Helium", "C"),
    ("How many continents?", "5", "6", "7", "8", "C"),
    ("Largest mammal?", "Elephant", "Blue Whale", "Giraffe", "Rhino", "B"),
    ("Currency of Japan?", "Yuan", "Won", "Yen", "Dollar", "C"),
    ("Fastest land animal?", "Lion", "Tiger", "Cheetah", "Leopard", "C"),
    ("Smallest prime number?", "0", "1", "2", "3", "C"),
    ("Chemical symbol for gold?", "Gd", "Au", "Ag", "Go", "B"),
    ("Which country invented pizza?", "France", "Italy", "Greece", "Spain", "B"),
    ("How many days in a leap year?", "364", "365", "366", "367", "C"),
    ("Which is the largest desert?", "Sahara", "Gobi", "Antarctic", "Kalahari", "C"),
    ("What does CPU stand for?", "Central Unit", "Computer Unit", "Central Processing Unit", "Core Unit", "C"),
    ("First man on moon?", "Aldrin", "Armstrong", "Gagarin", "Glenn", "B"),
]


# ═══ ENTRY ═══
@router.message(F.text.regexp(r"^/tgames(\s|$)"))
async def cmd_tgames(message: Message):
    await message.answer(
        "🎮 <b>ᴀꜱᴛʀᴀʟ ᴛ-ɢᴀᴍᴇꜱ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\nᴄʜᴏᴏꜱᴇ ᴀ ɢᴀᴍᴇ:",
        reply_markup=tgames_menu_kb()
    )


# ═══ QUIZ — Flow: menu → count → category → questions → result ═══
@router.callback_query(F.data == "tg:quiz")
async def quiz_select(cb: CallbackQuery):
    await cb.message.edit_text(
        "🧠 <b>ǫᴜɪᴢ</b>\n\nʜᴏᴡ ᴍᴀɴʏ ǫᴜᴇꜱᴛɪᴏɴꜱ?",
        reply_markup=quiz_count_kb()
    )
    await cb.answer()


@router.callback_query(F.data.startswith("qzcount:"))
async def quiz_count_selected(cb: CallbackQuery):
    count = int(cb.data.split(":")[1])
    QUIZ_CACHE[(cb.message.chat.id, cb.from_user.id)] = {
        "total": count, "done": 0, "score": 0, "correct": 0, "wrong": 0,
    }
    await cb.message.edit_text(
        f"🧠 <b>ǫᴜɪᴢ — {count} ǫᴜᴇꜱᴛɪᴏɴꜱ</b>\n\nᴄʜᴏᴏꜱᴇ ᴄᴀᴛᴇɢᴏʀʏ:",
        reply_markup=quiz_menu_kb()
    )
    await cb.answer()


@router.callback_query(F.data.startswith("quiz:"))
async def quiz_start(cb: CallbackQuery):
    cat = cb.data.split(":")[1]
    key = (cb.message.chat.id, cb.from_user.id)
    sess = QUIZ_CACHE.get(key)
    if not sess:
        # Fallback: default to 5 questions
        sess = {"total": 5, "done": 0, "score": 0, "correct": 0, "wrong": 0}
        QUIZ_CACHE[key] = sess

    await _send_quiz_question(cb, cat, key)


async def _send_quiz_question(cb: CallbackQuery, cat: str, key: tuple):
    sess = QUIZ_CACHE.get(key)
    if not sess:
        return await cb.answer("ꜱᴇꜱꜱɪᴏɴ ᴇxᴘɪʀᴇᴅ.", show_alert=True)

    if sess["done"] >= sess["total"]:
        return await _finish_quiz(cb, key)

    pool = QUIZ_SPACE if cat == "space" else QUIZ_GENERAL
    question, a, b, c, d, correct = random.choice(pool)
    qid = random.randint(100000, 999999)
    sess["current"] = (qid, correct, cat, question, a, b, c, d)

    await cb.message.edit_text(
        f"🧠 <b>{'ꜱᴘᴀᴄᴇ' if cat == 'space' else 'ɢᴇɴᴇʀᴀʟ'} ǫᴜɪᴢ</b>\n"
        f"ᴏ̨: <b>{sess['done'] + 1}/{sess['total']}</b>  |  ꜱᴄᴏʀᴇ: <b>{sess['score']}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>{question}</b>\n\nᴄʜᴏᴏꜱᴇ:",
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

    _, correct, cat, *_ = sess["current"]
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
        # -1 mark per 2 wrong
        if sess["wrong"] % 2 == 0:
            sess["score"] -= 1

    sess["done"] += 1

    if sess["done"] >= sess["total"]:
        return await _finish_quiz(cb, key)

    # Continue with next question
    await _send_quiz_question(cb, cat, key)


async def _finish_quiz(cb: CallbackQuery, key: tuple):
    sess = QUIZ_CACHE.pop(key, None)
    if not sess:
        return await cb.answer("ꜱᴇꜱꜱɪᴏɴ ᴇxᴘɪʀᴇᴅ.", show_alert=True)

    score = sess["score"]
    correct = sess["correct"]
    wrong = sess["wrong"]

    # Reward: correct answers * 40 coins minimum
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
        f"🪙 +{coins} ᴄᴏɪɴꜱ\n"
        f"📈 +{xp} xᴘ",
        reply_markup=back_main_kb()
    )
    await cb.answer("🏁")


# ═══ WORD GAME ═══
@router.callback_query(F.data == "tg:word")
async def word_start_via_menu(cb: CallbackQuery):
    user_id = cb.from_user.id
    attempts_used = await get_daily_word_attempts(user_id)
    if attempts_used >= DAILY_WORD_LIMIT:
        return await cb.answer(
            f"⏳ ᴅᴀɪʟʏ ʟɪᴍɪᴛ ʀᴇᴀᴄʜᴇᴅ ({attempts_used}/{DAILY_WORD_LIMIT})\n"
            f"ʀᴇꜱᴇᴛ ᴀᴛ ᴍɪᴅɴɪɢʜᴛ ᴜᴛᴄ", show_alert=True
        )

    word = get_random_5letter_word()
    key = (cb.message.chat.id, user_id)
    WORD_CACHE[key] = {"word": word, "attempts": 0, "history": [], "guessed": set()}
    await inc_word_attempt(user_id)
    new_count = await inc_daily_word_attempts(user_id)
    try:
        await mission_word_played(user_id)
    except Exception:
        pass

    remaining = DAILY_WORD_LIMIT - new_count

    await cb.message.edit_text(
        f"🔤 <b>ᴡᴏʀᴅ ɢᴜᴇꜱꜱɪɴɢ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📏 ʟᴇɴɢᴛʜ: <b>5 ʟᴇᴛᴛᴇʀꜱ</b>\n"
        f"🎯 ᴍᴀx ɢᴜᴇꜱꜱᴇꜱ: <b>30</b>\n"
        f"🎫 ᴛᴏᴅᴀʏ ᴀᴛᴛᴇᴍᴘᴛꜱ ʟᴇꜰᴛ: <b>{remaining}/{DAILY_WORD_LIMIT}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ᴛʏᴘᴇ ʏᴏᴜʀ 5-ʟᴇᴛᴛᴇʀ ᴡᴏʀᴅ ɪɴ ᴄʜᴀᴛ:"
    )
    await cb.answer()


@router.message(F.text.regexp(r"^/new(\s|$)"))
async def cmd_new(message: Message):
    args = message.text.split(maxsplit=1)
    user_id = message.from_user.id

    if len(args) > 1 and args[1].strip().lower() == "end":
        if message.chat.type == "private":
            return await message.reply("📩 ᴜꜱᴇ 🛑 ɢɪᴠᴇ ᴜᴘ ʙᴜᴛᴛᴏɴ ɪɴ ᴅᴍ.")
        # Group admin check via Telegram
        try:
            member = await message.bot.get_chat_member(message.chat.id, user_id)
            from aiogram.types import ChatMemberOwner, ChatMemberAdministrator
            if not isinstance(member, (ChatMemberOwner, ChatMemberAdministrator)):
                return await message.reply("❌ ꜱᴏɴʟʏ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴇɴᴅ ɢᴀᴍᴇꜱ.")
        except Exception:
            return await message.reply("❌ ꜱᴏɴʟʏ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴇɴᴅ ɢᴀᴍᴇꜱ.")
        to_remove = [k for k in WORD_CACHE if k[0] == message.chat.id]
        for k in to_remove:
            WORD_CACHE.pop(k, None)
        return await message.reply("🛑 ᴀʟʟ ᴀᴄᴛɪᴠᴇ ɢᴀᴍᴇꜱ ᴇɴᴅᴇᴅ ɪɴ ᴛʜɪꜱ ᴄʜᴀᴛ.")

    attempts_used = await get_daily_word_attempts(user_id)
    if attempts_used >= DAILY_WORD_LIMIT:
        return await message.reply(
            f"⏳ <b>ᴅᴀɪʟʏ ʟɪᴍɪᴛ ʀᴇᴀᴄʜᴇᴅ</b>\n"
            f"ʏᴏᴜ'ᴠᴇ ᴜꜱᴇᴅ <b>{attempts_used}/{DAILY_WORD_LIMIT}</b> ᴀᴛᴛᴇᴍᴘᴛꜱ ᴛᴏᴅᴀʏ.\n"
            f"ʀᴇꜱᴇᴛ ᴀᴛ ᴍɪᴅɴɪɢʜᴛ ᴜᴛᴄ."
        )

    word = get_random_5letter_word()
    key = (message.chat.id, user_id)
    WORD_CACHE[key] = {"word": word, "attempts": 0, "history": [], "guessed": set()}
    await inc_word_attempt(user_id)
    new_count = await inc_daily_word_attempts(user_id)
    try:
        await mission_word_played(user_id)
    except Exception:
        pass

    remaining = DAILY_WORD_LIMIT - new_count

    await message.answer(
        f"🔤 <b>ᴡᴏʀᴅ ɢᴜᴇꜱꜱɪɴɢ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📏 ʟᴇɴɢᴛʜ: <b>5 ʟᴇᴛᴛᴇʀꜱ</b>\n"
        f"🎯 ᴍᴀx ɢᴜᴇꜱꜱᴇꜱ: <b>30</b>\n"
        f"🎫 ᴛᴏᴅᴀʏ ᴀᴛᴛᴇᴍᴘᴛꜱ ʟᴇꜰᴛ: <b>{remaining}/{DAILY_WORD_LIMIT}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ᴛʏᴘᴇ ʏᴏᴜʀ 5-ʟᴇᴛᴛᴇʀ ᴡᴏʀᴅ ɪɴ ᴄʜᴀᴛ:"
    )


def _render_history(history):
    lines = []
    for word, colors in history:
        emoji = {"g": "🟩", "y": "🟨", "x": "⬛"}
        chars = " ".join(c.upper() for c in word)
        boxes = " ".join(emoji[c] for c in colors)
        lines.append(f"<code>{chars}</code>\n{boxes}")
    return "\n".join(lines)


def _evaluate(word, guess):
    result = ["x"] * 5
    wc, gc = list(word), list(guess)
    for i in range(5):
        if gc[i] == wc[i]:
            result[i] = "g"; wc[i] = None; gc[i] = None
    for i in range(5):
        if gc[i] and gc[i] in wc:
            result[i] = "y"; wc[wc.index(gc[i])] = None
    return result


@router.message(F.text & ~F.text.startswith("/"))
async def word_guess(message: Message):
    if not message.text:
        raise SkipHandler()

    key = (message.chat.id, message.from_user.id)
    game = WORD_CACHE.get(key)
    if not game:
        raise SkipHandler()

    guess = message.text.strip().lower()

    # Length / alpha check
    if len(guess) != 5 or not guess.isalpha():
        return await message.reply("❌ ꜱᴇɴᴅ ᴀ ᴠᴀʟɪᴅ 5-ʟᴇᴛᴛᴇʀ ᴡᴏʀᴅ.")
    # All-same-letter rejection
    if len(set(guess)) == 1:
        return await message.reply("❌ ᴛʜᴀᴛ'ꜱ ɴᴏᴛ ᴀ ᴠᴀʟɪᴅ ᴡᴏʀᴅ.")
    # Duplicate rejection
    if guess in game.get("guessed", set()):
        return await message.reply(f"⚠️ <b>{guess.upper()}</b> ᴀʟʀᴇᴀᴅʏ ɢᴜᴇꜱꜱᴇᴅ. ᴛʀʏ ᴀ ɴᴇᴡ ᴡᴏʀᴅ.")
    # Dictionary check
    if not is_valid_word(guess):
        return await message.reply(f"❌ <b>{guess.upper()}</b> ɪꜱ ɴᴏᴛ ᴀ ᴠᴀʟɪᴅ ᴇɴɢʟɪꜱʜ ᴡᴏʀᴅ.")

    game["guessed"].add(guess)
    colors = _evaluate(game["word"], guess)
    game["history"].append((guess, colors))
    game["attempts"] += 1

    # WIN → end game immediately
    if all(c == "g" for c in colors):
        attempts = game["attempts"]
        reward = max(10, WORD_MAX_REWARD // attempts) if attempts > 1 else WORD_MAX_REWARD
        await add_coins(message.from_user.id, reward)
        await inc_word_solved(message.from_user.id, reward)
        WORD_CACHE.pop(key, None)
        return await message.reply(
            f"🎉 <b>ᴄᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴꜱ!</b>\n"
            f"ʏᴏᴜ ɢᴜᴇꜱꜱᴇᴅ ᴛʜᴇ ᴄᴏʀʀᴇᴄᴛ ᴡᴏʀᴅ!\n\n"
            f"ᴛʜᴇ ᴡᴏʀᴅ ᴡᴀꜱ: <b>{game['word'].upper()}</b>\n"
            f"ᴀᴛᴛᴇᴍᴘᴛꜱ: <b>{attempts}</b>\n\n"
            f"🪙 +{reward} ᴄᴏɪɴꜱ"
        )

    if game["attempts"] >= 30:
        word = game["word"]
        WORD_CACHE.pop(key, None)
        return await message.reply(f"💀 ɢᴀᴍᴇ ᴏᴠᴇʀ! ᴛʜᴇ ᴡᴏʀᴅ ᴡᴀꜱ <b>{word.upper()}</b>")

    await message.reply(
        f"🔤 <b>ᴡᴏʀᴅ ɢᴜᴇꜱꜱɪɴɢ</b>\n"
        f"🎯 ᴀᴛᴛᴇᴍᴘᴛꜱ: <b>{game['attempts']}/30</b>\n\n"
        f"{_render_history(game['history'])}\n\n"
        f"ᴛʏᴘᴇ ɴᴇxᴛ ɢᴜᴇꜱꜱ (5 ʟᴇᴛᴛᴇʀꜱ):"
    )


# ═══ NUMBER GUESSING — /h ═══
@router.callback_query(F.data == "tg:number")
async def number_start(cb: CallbackQuery):
    secret = random.randint(100, 500)
    key = (cb.message.chat.id, cb.from_user.id)
    NUMBER_CACHE[key] = {"secret": secret, "attempts": 0}
    await inc_number_attempt(cb.from_user.id)
    await cb.message.edit_text(
        "🔢 <b>ɢᴜᴇꜱꜱ ᴛʜᴇ ɴᴜᴍʙᴇʀ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🎯 ʀᴀɴɢᴇ: <b>100–500</b>\n"
        "🎲 ᴍᴀx ᴄʜᴀɴᴄᴇꜱ: <b>12</b>\n\n"
        "ᴜꜱᴇ <code>/h &lt;ɴᴜᴍʙᴇʀ&gt;</code> ᴛᴏ ɢᴜᴇꜱꜱ.\n"
        "ᴇxᴀᴍᴘʟᴇ: <code>/h 250</code>"
    )
    await cb.answer()


@router.message(F.text.regexp(r"^/h(\s|$)"))
async def number_guess(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip().isdigit():
        return await message.reply("ᴜꜱᴀɢᴇ: <code>/h 250</code>")

    user_id = message.from_user.id
    key = (message.chat.id, user_id)
    game = NUMBER_CACHE.get(key)
    if not game:
        return await message.reply("❌ ꜱᴛᴀʀᴛ ᴀ ɢᴀᴍᴇ ᴠɪᴀ /tgames ꜰɪʀꜱᴛ.")

    guess = int(parts[1].strip())
    if not (100 <= guess <= 500):
        return await message.reply("❌ ɢᴜᴇꜱꜱ ʙᴇᴛᴡᴇᴇɴ 100 ᴀɴᴅ 500.")

    game["attempts"] += 1
    await inc_number_guess(user_id)
    secret = game["secret"]

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

    if game["attempts"] >= 12:
        NUMBER_CACHE.pop(key, None)
        return await message.reply(f"💀 ɢᴀᴍᴇ ᴏᴠᴇʀ! ꜱᴇᴄʀᴇᴛ ᴡᴀꜱ <b>{secret}</b>")

    if guess < secret:
        await message.reply(f"⬆️ <b>{guess} ɪꜱ ᴠᴇʀʏ ʟᴏᴡ</b>\nʀᴀɴɢᴇ: {guess}–500\nᴀᴛᴛᴇᴍᴘᴛꜱ: {game['attempts']}/12")
    else:
        await message.reply(f"⬇️ <b>{guess} ɪꜱ ᴠᴇʀʏ ʜɪɢʜ</b>\nʀᴀɴɢᴇ: 100–{guess}\nᴀᴛᴛᴇᴍᴘᴛꜱ: {game['attempts']}/12")
