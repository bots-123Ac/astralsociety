import json
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from keyboards.game_kb import (
    games_menu_kb, word_length_kb, word_game_kb, leaderboard_menu_kb,
)
from keyboards.main_menu import back_kb
from utils.database import (
    start_word_game, get_word_game, update_word_game, end_word_game,
    add_points, add_coins, get_word_leaderboard,
)
from utils.words import get_random_word, words_count
from utils.ui import smart_edit

router = Router()

MAX_ATTEMPTS = 30


# ═══════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════
def score_for_attempt(attempts: int) -> int:
    """Fewer attempts = more points. Attempt 1 = 300 pts, min 10."""
    if attempts <= 1:
        return 300
    return max(10, 300 // attempts)


def evaluate_guess(word: str, guess: str) -> list:
    """
    Returns list of colors.
    'green'  = correct letter + position
    'yellow' = correct letter, wrong position
    'grey'   = letter not in word
    """
    result = ["grey"] * len(word)
    word_chars = list(word)
    guess_chars = list(guess)

    # Pass 1: mark greens
    for i in range(len(word)):
        if guess_chars[i] == word_chars[i]:
            result[i] = "green"
            word_chars[i] = None
            guess_chars[i] = None

    # Pass 2: mark yellows
    for i in range(len(word)):
        if guess_chars[i] and guess_chars[i] in word_chars:
            result[i] = "yellow"
            word_chars[word_chars.index(guess_chars[i])] = None

    return result


def render_guess(guess: str, colors: list) -> str:
    emoji = {"green": "🟩", "yellow": "🟨", "grey": "⬛"}
    chars = " ".join(c.upper() for c in guess)
    boxes = " ".join(emoji[c] for c in colors)
    return f"<code>{chars}</code>\n{boxes}"


def game_status_text(word_length, attempts, max_attempts, history_lines):
    return (
        f"🔤 <b>ᴡᴏʀᴅ ɢᴜᴇssɪɴɢ ɢᴀᴍᴇ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📏 ʟᴇɴɢᴛʜ: <b>{word_length}</b> ʟᴇᴛᴛᴇʀs\n"
        f"🎯 ᴀᴛᴛᴇᴍᴘᴛs: <b>{attempts}/{max_attempts}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{chr(10).join(history_lines)}\n\n"
        f"ᴛʏᴘᴇ ʏᴏᴜʀ ɢᴜᴇss ({word_length} ʟᴇᴛᴛᴇʀs):"
    )


# ═══════════════════════════════════════════════
# 🎮 GAMES MENU
# ═══════════════════════════════════════════════
@router.callback_query(F.data == "menu:games")
async def games_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    text = (
        "🎮 <b>ɢᴀᴍᴇs sᴇᴄᴛɪᴏɴ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "ᴄʜᴏᴏsᴇ ᴀ ɢᴀᴍᴇ ᴛᴏ ᴘʟᴀʏ:\n\n"
        "🔤 ᴡᴏʀᴅ ɢᴜᴇssɪɴɢ — ɢᴜᴇss ᴛʜᴇ ᴡᴏʀᴅ, ᴇᴀʀɴ ᴘᴏɪɴᴛs\n\n"
        "ᴍᴏʀᴇ ɢᴀᴍᴇs ᴄᴏᴍɪɴɢ sᴏᴏɴ ✨"
    )
    await smart_edit(cb, text, games_menu_kb())
    await cb.answer()


# ═══════════════════════════════════════════════
# 🔤 WORD GAME
# ═══════════════════════════════════════════════
@router.callback_query(F.data == "wg:menu")
async def wg_menu(cb: CallbackQuery, state: FSMContext):
    counts = words_count()
    text = (
        "🔤 <b>ᴡᴏʀᴅ ɢᴜᴇssɪɴɢ ɢᴀᴍᴇ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🟩 ᴄᴏʀʀᴇᴄᴛ ʟᴇᴛᴛᴇʀ + ᴘᴏsɪᴛɪᴏɴ\n"
        "🟨 ᴄᴏʀʀᴇᴄᴛ ʟᴇᴛᴛᴇʀ, ᴡʀᴏɴɢ ᴘᴏsɪᴛɪᴏɴ\n"
        "⬛ ʟᴇᴛᴛᴇʀ ɴᴏᴛ ɪɴ ᴡᴏʀᴅ\n\n"
        "🎯 ᴍᴀx ᴀᴛᴛᴇᴍᴘᴛs: 30\n"
        "⭐ ғᴇᴡᴇʀ ᴀᴛᴛᴇᴍᴘᴛs = ᴍᴏʀᴇ ᴘᴏɪɴᴛs\n\n"
        f"📚 ᴡᴏʀᴅ ᴘᴏᴏʟ:\n"
        f"   • 4 ʟᴇᴛᴛᴇʀs — {counts.get(4, 0)} ᴡᴏʀᴅs\n"
        f"   • 5 ʟᴇᴛᴛᴇʀs — {counts.get(5, 0)} ᴡᴏʀᴅs\n"
        f"   • 6 ʟᴇᴛᴛᴇʀs — {counts.get(6, 0)} ᴡᴏʀᴅs\n\n"
        "ᴄʜᴏᴏsᴇ ᴡᴏʀᴅ ʟᴇɴɢᴛʜ:"
    )
    await smart_edit(cb, text, word_length_kb())
    await cb.answer()


@router.callback_query(F.data.startswith("wg:new:"))
async def wg_new(cb: CallbackQuery, state: FSMContext):
    try:
        length = int(cb.data.split(":")[2])
    except (ValueError, IndexError):
        await cb.answer("ɪɴᴠᴀʟɪᴅ ʟᴇɴɢᴛʜ", show_alert=True)
        return

    if length not in (4, 5, 6):
        await cb.answer("ɪɴᴠᴀʟɪᴅ", show_alert=True)
        return

    word = get_random_word(length)
    await start_word_game(cb.from_user.id, word, length)

    text = game_status_text(length, 0, MAX_ATTEMPTS, ["🎯 sᴛᴀʀᴛ ɢᴜᴇssɪɴɢ!"])
    await smart_edit(cb, text, word_game_kb())
    await cb.answer(f"🎮 ɢᴀᴍᴇ sᴛᴀʀᴛᴇᴅ! {length} ʟᴇᴛᴛᴇʀs")


@router.callback_query(F.data == "wg:status")
async def wg_status(cb: CallbackQuery):
    row = await get_word_game(cb.from_user.id)
    if not row:
        await cb.answer("ɴᴏ ᴀᴄᴛɪᴠᴇ ɢᴀᴍᴇ", show_alert=True)
        return
    word, length, attempts, max_a, status, guesses_json = row
    guesses = json.loads(guesses_json or "[]")
    history = [render_guess(g["word"], g["colors"]) for g in guesses]
    if not history:
        history = ["🎯 sᴛᴀʀᴛ ɢᴜᴇssɪɴɢ!"]
    text = game_status_text(length, attempts, max_a, history)
    await smart_edit(cb, text, word_game_kb())
    await cb.answer()


@router.callback_query(F.data == "wg:giveup")
async def wg_giveup(cb: CallbackQuery):
    row = await get_word_game(cb.from_user.id)
    if not row:
        await cb.answer("ɴᴏ ᴀᴄᴛɪᴠᴇ ɢᴀᴍᴇ", show_alert=True)
        return
    word, length, attempts, _, _, _ = row
    await end_word_game(cb.from_user.id, word, attempts, False, 0)
    text = (
        f"🛑 <b>ɢᴀᴍᴇ ᴇɴᴅᴇᴅ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ᴛʜᴇ ᴡᴏʀᴅ ᴡᴀs: <b>{word.upper()}</b>\n"
        f"ᴀᴛᴛᴇᴍᴘᴛs ᴜsᴇᴅ: <b>{attempts}</b>"
    )
    await smart_edit(cb, text, games_menu_kb())
    await cb.answer()


# ═══════════════════════════════════════════════
# 🎯 /new COMMAND
# ═══════════════════════════════════════════════
@router.message(Command("new"))
async def cmd_new(message: Message, state: FSMContext):
    text = (
        "🔤 <b>ᴡᴏʀᴅ ɢᴜᴇssɪɴɢ ɢᴀᴍᴇ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "ᴄʜᴏᴏsᴇ ᴡᴏʀᴅ ʟᴇɴɢᴛʜ:"
    )
    await message.answer(text, reply_markup=word_length_kb())


# ═══════════════════════════════════════════════
# ✏️ GUESS HANDLER
# ═══════════════════════════════════════════════
@router.message(F.text & ~F.text.startswith("/"))
async def handle_guess(message: Message, state: FSMContext):
    """
    Capture guesses ONLY if user has an active game in PM.
    Otherwise silently ignore (no conflict with other handlers).
    """
    if message.chat.type != "private":
        return

    row = await get_word_game(message.from_user.id)
    if not row:
        return

    word, length, attempts, max_a, status, guesses_json = row
    if status != "active":
        return

    guess = (message.text or "").strip().lower()

    if len(guess) != length or not guess.isalpha():
        await message.answer(
            f"❌ sᴇɴᴅ ᴀ <b>{length}-ʟᴇᴛᴛᴇʀ</b> ᴡᴏʀᴅ (ᴏɴʟʏ ʟᴇᴛᴛᴇʀs)."
        )
        return

    colors = evaluate_guess(word, guess)
    guesses = json.loads(guesses_json or "[]")
    guesses.append({"word": guess, "colors": colors})
    attempts += 1

    # ─── WIN ───
    if all(c == "green" for c in colors):
        score = score_for_attempt(attempts)
        await end_word_game(message.from_user.id, word, attempts, True, score)
        await add_points(message.from_user.id, score)
        await add_coins(message.from_user.id, score // 2)

        text = (
            f"🎉 <b>ʏᴏᴜ ᴡᴏɴ!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"ᴛʜᴇ ᴡᴏʀᴅ ᴡᴀs: <b>{word.upper()}</b>\n"
            f"ᴀᴛᴛᴇᴍᴘᴛs: <b>{attempts}</b>\n\n"
            f"⭐ ᴘᴏɪɴᴛs: <b>+{score}</b>\n"
            f"🪙 ᴄᴏɪɴs: <b>+{score // 2}</b>"
        )
        await message.answer(text)
        return

    # ─── LOSS ───
    if attempts >= max_a:
        await end_word_game(message.from_user.id, word, attempts, False, 0)
        await message.answer(
            f"💀 <b>ɢᴀᴍᴇ ᴏᴠᴇʀ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"ᴛʜᴇ ᴡᴏʀᴅ ᴡᴀs: <b>{word.upper()}</b>\n"
            f"ʙᴇᴛᴛᴇʀ ʟᴜᴄᴋ ɴᴇxᴛ ᴛɪᴍᴇ!"
        )
        return

    # ─── CONTINUE ───
    await update_word_game(
        message.from_user.id, attempts, "active", json.dumps(guesses)
    )
    history = [render_guess(g["word"], g["colors"]) for g in guesses]
    text = game_status_text(length, attempts, max_a, history)
    await message.answer(text, reply_markup=word_game_kb())


# ═══════════════════════════════════════════════
# 🏆 LEADERBOARD
# ═══════════════════════════════════════════════
@router.callback_query(F.data == "menu:lb")
async def lb_menu(cb: CallbackQuery):
    text = "🏆 <b>ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ</b>\n━━━━━━━━━━━━━━━━━━━━━\n\nᴄʜᴏᴏsᴇ ᴄᴀᴛᴇɢᴏʀʏ:"
    await smart_edit(cb, text, leaderboard_menu_kb())
    await cb.answer()


@router.callback_query(F.data == "lb:word")
async def lb_word(cb: CallbackQuery):
    rows = await get_word_leaderboard(10)
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

    if not rows:
        body = "ηᴏ sᴄᴏʀᴇs ʏᴇᴛ.\n\nʙᴇ ᴛʜᴇ ғɪʀsᴛ ᴛᴏ ᴘʟᴀʏ!"
    else:
        lines = []
        for i, (name, uname, score) in enumerate(rows):
            display = f"@{uname}" if uname else name
            lines.append(f"{medals[i]} {display} — <b>{score}</b> ᴘᴛs")
        body = "\n".join(lines)

    text = (
        f"🏆 <b>ᴡᴏʀᴅ ɢᴀᴍᴇ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ᴛᴏᴘ 10 ᴘʟᴀʏᴇʀs:\n\n{body}"
    )
    await smart_edit(cb, text, leaderboard_menu_kb())
    await cb.answer()


@router.callback_query(F.data == "lb:quiz")
async def lb_quiz(cb: CallbackQuery):
    text = (
        f"🏆 <b>ǫᴜɪᴢ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ᴜsᴇ /profile ᴛᴏ sᴇᴇ ʏᴏᴜʀ ᴏᴡɴ sᴛᴀᴛs.\n\n"
        f"sᴜʙᴊᴇᴄᴛ-ᴡɪsᴇ ʀᴀɴᴋɪɴɢ ᴄᴏᴍɪɴɢ sᴏᴏɴ ✨"
    )
    await smart_edit(cb, text, leaderboard_menu_kb())
    await cb.answer()
