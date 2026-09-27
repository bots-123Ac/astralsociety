import random
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.event.bases import SkipHandler

from config import (
    QUIZ_REWARD_COINS, NUMBER_REWARD_COINS, WORD_MAX_REWARD,
)
from keyboards.main_menu import (
    tgames_menu_kb, quiz_menu_kb, quiz_options_kb, back_main_kb,
)
from utils.words import get_random_5letter_word
from utils.database import (
    add_coins, add_xp, inc_quiz_attempt, inc_quiz_solved,
    inc_word_attempt, inc_word_solved, inc_number_attempt, inc_number_guess,
    has_xp_boost, mission_word_played,
)
from utils.permissions import is_bot_admin

router = Router()

# ═══════════════════════════════════════════════
# SESSION CACHES — keyed by (chat_id, user_id)
# This ensures DM and Group sessions are isolated
# ═══════════════════════════════════════════════
QUIZ_CACHE = {}      # (chat_id, user_id) -> (qid, correct, category)
WORD_CACHE = {}      # (chat_id, user_id) -> {word, attempts, history}
NUMBER_CACHE = {}    # (chat_id, user_id) -> {secret, attempts}


QUIZ_SPACE = [
    ("Which planet is known as the Red Planet?", "Venus", "Mars", "Jupiter", "Saturn", "B"),
    ("Which is the largest planet in our solar system?", "Earth", "Saturn", "Jupiter", "Neptune", "C"),
    ("How many moons does Earth have?", "1", "2", "3", "0", "A"),
    ("Which planet has the most moons?", "Jupiter", "Saturn", "Uranus", "Neptune", "B"),
    ("What is the closest planet to the Sun?", "Venus", "Earth", "Mercury", "Mars", "C"),
    ("Which planet has rings?", "Mars", "Saturn", "Venus", "Mercury", "B"),
    ("What galaxy is Earth in?", "Andromeda", "Milky Way", "Sombrero", "Whirlpool", "B"),
    ("Which planet is hottest?", "Mercury", "Venus", "Mars", "Jupiter", "B"),
    ("How many planets in solar system?", "7", "8", "9", "10", "B"),
    ("Which planet spins fastest?", "Earth", "Jupiter", "Saturn", "Mars", "B"),
]

QUIZ_GENERAL = [
    ("What is the capital of France?", "London", "Paris", "Rome", "Berlin", "B"),
    ("Who wrote Romeo and Juliet?", "Dickens", "Shakespeare", "Tolstoy", "Twain", "B"),
    ("Largest ocean on Earth?", "Atlantic", "Indian", "Pacific", "Arctic", "C"),
    ("Which gas do plants absorb?", "Oxygen", "Nitrogen", "CO2", "Helium", "C"),
    ("How many continents?", "5", "6", "7", "8", "C"),
    ("Largest mammal?", "Elephant", "Blue Whale", "Giraffe", "Rhino", "B"),
    ("Currency of Japan?", "Yuan", "Won", "Yen", "Dollar", "C"),
    ("Fastest land animal?", "Lion", "Tiger", "Cheetah", "Leopard", "C"),
    ("Smallest prime number?", "0", "1", "2", "3", "C"),
    ("Chemical symbol for gold?", "Gd", "Au", "Ag", "Go", "B"),
]


# ═══════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════
@router.message(F.text.regexp(r"^/tgames(\s|$)"))
async def cmd_tgames(message: Message):
    await message.answer(
        "🎮 <b>ᴧsᴛʀᴧʟ т-ɢᴧϻєs</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "ᴄнσσsє ᴧ ɢᴧϻє:",
        reply_markup=tgames_menu_kb()
    )


# ═══ QUIZ ═══
@router.callback_query(F.data == "tg:quiz")
async def quiz_select(cb: CallbackQuery):
    await cb.message.edit_text(
        "🧠 <b>ǫᴜiᴢ</b>\n\nᴄнσσsє ᴄᴧтєɢσʀʏ:",
        reply_markup=quiz_menu_kb()
    )
    await cb.answer()


@router.callback_query(F.data.startswith("quiz:"))
async def quiz_start(cb: CallbackQuery):
    cat = cb.data.split(":")[1]
    if cat not in ("space", "general"):
        return await cb.answer()
    pool = QUIZ_SPACE if cat == "space" else QUIZ_GENERAL
    question, a, b, c, d, correct = random.choice(pool)
    qid = random.randint(10000, 99999)
    key = (cb.message.chat.id, cb.from_user.id)
    QUIZ_CACHE[key] = (qid, correct, cat)

    await cb.message.edit_text(
        f"🧠 <b>{'sᴩᴧᴄє' if cat == 'space' else 'ɢєηєʀᴧʟ'} ǫᴜiᴢ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>{question}</b>\n\n"
        f"ᴄнσσsє ᴧη σᴩᴛiση:",
        reply_markup=quiz_options_kb(qid, a, b, c, d)
    )
    await cb.answer()


@router.callback_query(F.data.startswith("qans:"))
async def quiz_answer(cb: CallbackQuery):
    parts = cb.data.split(":")
    qid, selected = int(parts[1]), parts[2]
    key = (cb.message.chat.id, cb.from_user.id)
    data = QUIZ_CACHE.get(key)
    if not data or data[0] != qid:
        return await cb.answer("sєssiση єxᴩiʀєᴅ.", show_alert=True)
    _, correct, cat = data
    await inc_quiz_attempt(cb.from_user.id)
    boost = await has_xp_boost(cb.from_user.id)
    if selected == correct:
        coins = QUIZ_REWARD_COINS
        xp_gain = random.randint(0, 5)
        if boost:
            xp_gain *= 2
        await add_coins(cb.from_user.id, coins)
        await add_xp(cb.from_user.id, xp_gain)
        await inc_quiz_solved(cb.from_user.id)
        result = f"✅ <b>ᴄσʀʀєᴄт!</b>\n\n🪙 +{coins} ᴄσiηs\n📈 +{xp_gain} xᴩ"
    else:
        result = f"❌ <b>ᴡʀσηɢ!</b>\n\nᴄσʀʀєᴄт: <b>{correct}</b>"
    QUIZ_CACHE.pop(key, None)
    await cb.message.edit_text(
        f"🧠 ǫᴜiᴢ ʀєsᴜʟт\n━━━━━━━━━━━━━━━━━━━━━\n\n{result}",
        reply_markup=back_main_kb()
    )
    await cb.answer("✅" if selected == correct else "❌")


# ═══════════════════════════════════════════════
# 🔤 WORD GUESSING — isolated per (chat_id, user_id)
# ═══════════════════════════════════════════════
@router.callback_query(F.data == "tg:word")
async def word_start(cb: CallbackQuery):
    word = get_random_5letter_word()
    key = (cb.message.chat.id, cb.from_user.id)
    WORD_CACHE[key] = {"word": word, "attempts": 0, "history": []}
    await inc_word_attempt(cb.from_user.id)
    try:
        await mission_word_played(cb.from_user.id)
    except Exception:
        pass

    text = (
        f"🔤 <b>ᴡσʀᴅ ɢᴜєssiηɢ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📏 ʟєηɢтн: <b>5 ʟєттєʀs</b>\n"
        f"🎯 ϻᴧx ᴄнᴧηᴄєs: <b>30</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ᴛʏᴩє ʏσᴜʀ 5-ʟєттєʀ ωσʀᴅ iη ᴄнᴧт:"
    )
    await cb.message.edit_text(text)
    await cb.answer()


@router.message(F.text.regexp(r"^/new(\s|$)"))
async def cmd_new(message: Message):
    args = message.text.split(maxsplit=1)
    length = 5  # default
    if len(args) > 1:
        arg = args[1].strip().lower()
        if arg == "end":
            # Only in group: admin can end all games
            if message.chat.type == "private":
                return await message.reply("📩 ᴜsє 🛑 ɢivє ᴜᴩ ʙᴜᴛᴛᴏɴ iη ᴅᴍ.")
            if not is_bot_admin(message.from_user.id):
                # Check if group admin
                try:
                    member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
                    from aiogram.types import ChatMemberOwner, ChatMemberAdministrator
                    if not isinstance(member, (ChatMemberOwner, ChatMemberAdministrator)):
                        return await message.reply("❌ sσηʟʏ ɢʀσᴜᴩ ᴧᴅϻiηs ᴄᴧη ᴇηᴅ ɢᴧϻєs.")
                except Exception:
                    return await message.reply("❌ sσηʟʏ ɢʀσᴜᴩ ᴧᴅϻiηs ᴄᴧη ᴇηᴅ ɢᴧϻєs.")
            # Clear all games in this chat
            to_remove = [k for k in WORD_CACHE if k[0] == message.chat.id]
            for k in to_remove:
                WORD_CACHE.pop(k, None)
            to_remove_n = [k for k in NUMBER_CACHE if k[0] == message.chat.id]
            for k in to_remove_n:
                NUMBER_CACHE.pop(k, None)
            return await message.reply("🛑 ᴧʟʟ ᴀᴄᴛɪᴠᴇ ɢᴀᴍᴇs ᴇηᴅᴇᴅ ɪη ᴛʜɪs ᴄʜᴀᴛ.")

    word = get_random_5letter_word()
    key = (message.chat.id, message.from_user.id)
    WORD_CACHE[key] = {"word": word, "attempts": 0, "history": []}
    await inc_word_attempt(message.from_user.id)
    try:
        await mission_word_played(message.from_user.id)
    except Exception:
        pass

    text = (
        f"🔤 <b>ᴡσʀᴅ ɢᴜєssiηɢ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📏 ʟєηɢтн: <b>5 ʟєттєʀs</b>\n"
        f"🎯 ϻᴧx ᴄнᴧηᴄєs: <b>30</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ᴛʏᴩє ʏσᴜʀ 5-ʟєттєʀ ωσʀᴅ iη ᴄнᴧт:"
    )
    await message.answer(text)


def _render_word_history(history):
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

    # ═══ SESSION KEY: (chat_id, user_id) — this is the fix ═══
    key = (message.chat.id, message.from_user.id)
    game = WORD_CACHE.get(key)
    if not game:
        raise SkipHandler()  # No active game → next router

    guess = message.text.strip().lower()
    if len(guess) != 5 or not guess.isalpha():
        return await message.reply("❌ sєηᴅ ᴧ <b>5-ʟєттєʀ</b> ωσʀᴅ.")

    colors = _evaluate(game["word"], guess)
    game["history"].append((guess, colors))
    game["attempts"] += 1

    if all(c == "g" for c in colors):
        attempts = game["attempts"]
        reward = max(10, WORD_MAX_REWARD // attempts) if attempts > 1 else WORD_MAX_REWARD
        await add_coins(message.from_user.id, reward)
        await inc_word_solved(message.from_user.id, reward)
        WORD_CACHE.pop(key, None)
        return await message.reply(
            f"🎉 <b>ʏσᴜ ωση!</b>\n\nᴛнє ωσʀᴅ: <b>{game['word'].upper()}</b>\n"
            f"ᴧттєϻᴩтs: <b>{attempts}</b>\n\n🪙 +{reward} ᴄσiηs"
        )

    if game["attempts"] >= 30:
        word = game["word"]
        WORD_CACHE.pop(key, None)
        return await message.reply(f"💀 ɢᴧϻє σᴠєʀ! ωσʀᴅ ωᴧs: <b>{word.upper()}</b>")

    await message.reply(
        f"🔤 <b>ᴡσʀᴅ ɢᴜєssiηɢ</b>\n"
        f"🎯 ᴧттєϻᴩтs: <b>{game['attempts']}/30</b>\n\n"
        f"{_render_word_history(game['history'])}\n\n"
        f"ᴛʏᴩє ηєxт ɢᴜєss (5 ʟєттєʀs):"
    )


# ═══ NUMBER ═══
@router.callback_query(F.data == "tg:number")
async def number_start(cb: CallbackQuery):
    secret = random.randint(100, 500)
    key = (cb.message.chat.id, cb.from_user.id)
    NUMBER_CACHE[key] = {"secret": secret, "attempts": 0}
    await inc_number_attempt(cb.from_user.id)
    await cb.message.edit_text(
        "🔢 <b>ɢᴜєss тнє ηᴜϻвєʀ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🎯 ʀᴧηɢє: <b>100–500</b>\n"
        "🎲 ϻᴧx ᴄнᴧηᴄєs: <b>12</b>\n\n"
        "ᴜsє /h <ηᴜϻвєʀ> тσ ɢᴜєss.\nᴇx: <code>/h 250</code>"
    )
    await cb.answer()


@router.message(F.text.regexp(r"^/h(\s|$)"))
async def number_guess(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip().isdigit():
        return await message.reply("ᴜsᴧɢє: <code>/h 250</code>")
    key = (message.chat.id, message.from_user.id)
    game = NUMBER_CACHE.get(key)
    if not game:
        return await message.reply("❌ sᴛᴧʀᴛ ɢᴧϻє ᴠiᴧ /tgames.")
    guess = int(parts[1].strip())
    if not (100 <= guess <= 500):
        return await message.reply("❌ ɢᴜєss 100–500.")
    game["attempts"] += 1
    await inc_number_guess(message.from_user.id)
    secret = game["secret"]
    if guess == secret:
        coins = NUMBER_REWARD_COINS
        xp_gain = random.randint(0, 12)
        if await has_xp_boost(message.from_user.id):
            xp_gain *= 2
        await add_coins(message.from_user.id, coins)
        await add_xp(message.from_user.id, xp_gain)
        NUMBER_CACHE.pop(key, None)
        return await message.reply(
            f"🎉 <b>ᴄσʀʀєᴄт!</b>\n\nsєᴄʀєт: <b>{secret}</b>\n"
            f"ᴧттєϻᴩтs: <b>{game['attempts']}</b>\n\n"
            f"🪙 +{coins} | 📈 +{xp_gain} xᴩ"
        )
    if game["attempts"] >= 12:
        NUMBER_CACHE.pop(key, None)
        return await message.reply(f"💀 ɢᴧᴍє σᴠєʀ! sєᴄʀєᴛ ωᴧs <b>{secret}</b>")
    if guess < secret:
        await message.reply(f"⬆️ <b>{guess} is ᴠєʀʏ ʟσω</b>\nʀᴧηɢє: {guess}–500\nᴀᴛᴛᴇᴍᴘᴛs: {game['attempts']}/12")
    else:
        await message.reply(f"⬇️ <b>{guess} is ᴠєʀʏ нiɢн</b>\nʀᴧηɢє: 100–{guess}\nᴀᴛᴛᴇᴍᴘᴛs: {game['attempts']}/12")
