import random
import json
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from keyboards.game_kb import games_menu_kb, word_length_kb, word_game_kb
from keyboards.main_menu import back_kb
from utils.database import (
    start_word_game, get_word_game, update_word_game, end_word_game, add_points,
)
from utils.ui import smart_edit

router = Router()

WORDS = {
    4: ["word", "game", "book", "love", "time", "rain", "fire", "blue", "star", "moon",
        "gold", "leaf", "song", "fish", "bird", "door", "road", "tree", "wind", "snow"],
    5: ["apple", "house", "light", "water", "happy", "music", "earth", "tiger", "crown",
        "dream", "heart", "storm", "cloud", "brave", "smile", "paper", "stone", "green",
        "black", "white", "quick", "piano", "candy", "magic", "queen"],
    6: ["planet", "orange", "flower", "silver", "yellow", "purple", "friend", "school",
        "sunset", "forest", "garden", "market", "castle", "palace", "window", "animal",
        "summer", "winter", "spring", "autumn", "pirate", "dragon", "singer", "travel"],
}

MAX_ATTEMPTS = 30


def score_for_attempt(attempts: int) -> int:
    """Attempt 1 = 300 pts, halving down to minimum 10."""
    base = 300
    if attempts <= 1:
        return base
    score = max(10, base // attempts)
    return score


def evaluate_guess(word: str, guess: str) -> list:
    """Return list of colors: 'green'/'yellow'/grey'."""
    result = ["grey"] * len(word)
    word_chars = list(word)
    guess_chars = list(guess)
    # First pass: green
    for i in range(len(word)):
        if guess_chars[i] == word_chars[i]:
            result[i] = "green"
            word_chars[i] = None
            guess_chars[i] = None
    # Second pass: yellow
    for i in range(len(word)):
        if guess_chars[i] and guess_chars[i] in word_chars:
            result[i] = "yellow"
            word_chars[word_chars.index(guess_chars[i])] = None
    return result


def render_guess(guess: str, colors: list) -> str:
    """Format guess with emoji boxes."""
    emoji = {"green": "🟩", "yellow": "🟨", "grey": "⬛"}
    chars = " ".join(c.upper() for c in guess)
    boxes = " ".join(emoji[c] for c in colors)
    return f"<code>{chars}</code>\n{boxes}"


def game_status_text(word_length, attempts, max_attempts, history_lines):
    text = (
        f"🔤 <b>ᴡᴏʀᴅ ɢᴜᴇssɪɴɢ ɢᴀᴍᴇ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📏 ʟᴇɴɢᴛʜ: <b>{word_length}</b> ʟᴇᴛᴛᴇʀs\n"
        f"🎯 ᴀᴛᴛᴇᴍᴘᴛs: <b>{attempts}/{max_attempts}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{chr(10).join(history_lines)}\n\n"
        f"ᴛʏᴘᴇ ʏᴏᴜʀ ɢᴜᴇss ({word_length} ʟᴇᴛᴛᴇʀs):"
    )
    return text


@router.callback_query(F.data == "menu:games")
async def games_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    text = "🎮 <b>ɢᴀᴍᴇs</b>\n━━━━━━━━━━━━━━━━━━━━━\n\nᴄʜᴏᴏsᴇ ᴀ ɢᴀᴍᴇ:"
    await smart_edit(cb, text, games_menu_kb())
    await cb.answer()


@router.callback_query(F.data == "wg:menu")
async def wg_menu(cb: CallbackQuery, state: FSMContext):
    text = (
        "🔤 <b>ᴡᴏʀᴅ ɢᴜᴇssɪɴɢ ɢᴀᴍᴇ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🟩 ᴄᴏʀʀᴇᴄᴛ ʟᴇᴛᴛᴇʀ + ᴘᴏsɪᴛɪᴏɴ\n"
        "🟨 ᴄᴏʀʀᴇᴄᴛ ʟᴇᴛᴛᴇʀ, ᴡʀᴏɴɢ ᴘᴏsɪᴛɪᴏɴ\n"
        "⬛ ʟᴇᴛᴛᴇʀ ɴᴏᴛ ɪɴ ᴡᴏʀᴅ\n\n"
        "ᴄʜᴏᴏsᴇ ᴡᴏʀᴅ ʟᴇɴɢᴛʜ:"
    )
    await smart_edit(cb, text, word_length_kb())
    await cb.answer()


@router.callback_query(F.data.startswith("wg:new:"))
async def wg_new(cb: CallbackQuery, state: FSMContext):
    length = int(cb.data.split(":")[2])
    word = random.choice(WORDS.get(length, WORDS[5]))
    await start_word_game(cb.from_user.id, word, length)
    text = game_status_text(length, 0, MAX_ATTEMPTS, ["🎯 sᴛᴀʀᴛ ɢᴜᴇssɪɴɢ!"])
    await smart_edit(cb, text, word_game_kb())
    await cb.answer()


@router.callback_query(F.data == "wg:status")
async def wg_status(cb: CallbackQuery):
    row = await get_word_game(cb.from_user.id)
    if not row:
        await cb.answer("ɴᴏ ᴀᴄᴛɪᴠᴇ ɢᴀᴍᴇ", show_alert=True)
        return
    word, length, attempts, max_a, status, guesses_json = row
    guesses = json.loads(guesses_json or "[]")
    history = []
    for g in guesses:
        history.append(render_guess(g["word"], g["colors"]))
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
    text = f"🛑 <b>ɢᴀᴍᴇ ᴇɴᴅᴇᴅ</b>\n\nᴛʜᴇ ᴡᴏʀᴅ ᴡᴀs: <b>{word.upper()}</b>"
    await smart_edit(cb, text, games_menu_kb())
    await cb.answer()


@router.message(Command("new"))
async def cmd_new(message: Message, state: FSMContext):
    text = (
        "🔤 <b>ᴡᴏʀᴅ ɢᴜᴇssɪɴɢ ɢᴀᴍᴇ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\nᴄʜᴏᴏsᴇ ᴡᴏʀᴅ ʟᴇɴɢᴛʜ:"
    )
    await message.answer(text, reply_markup=word_length_kb())


# ─── MESSAGE HANDLER: capture guesses ───
@router.message(F.text & ~F.text.startswith("/"))
async def handle_guess(message: Message, state: FSMContext):
    row = await get_word_game(message.from_user.id)
    if not row:
        return  # Not in a game, ignore
    word, length, attempts, max_a, status, guesses_json = row
    if status != "active":
        return

    guess = message.text.strip().lower()
    if len(guess) != length or not guess.isalpha():
        await message.answer(f"❌ sᴇɴᴅ ᴀ {length}-ʟᴇᴛᴛᴇʀ ᴡᴏʀᴅ.")
        return

    colors = evaluate_guess(word, guess)
    guesses = json.loads(guesses_json or "[]")
    guesses.append({"word": guess, "colors": colors})
    attempts += 1

    # Check win
    if all(c == "green" for c in colors):
        score = score_for_attempt(attempts)
        await end_word_game(message.from_user.id, word, attempts, True, score)
        await add_points(message.from_user.id, score)
        await message.answer(
            f"🎉 <b>ʏᴏᴜ ᴡᴏɴ!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"ᴛʜᴇ ᴡᴏʀᴅ ᴡᴀs: <b>{word.upper()}</b>\n"
            f"ᴀᴛᴛᴇᴍᴘᴛs: <b>{attempts}</b>\n"
            f"⭐ ᴘᴏɪɴᴛs ᴇᴀʀɴᴇᴅ: <b>{score}</b>"
        )
        return

    # Check loss
    if attempts >= max_a:
        await end_word_game(message.from_user.id, word, attempts, False, 0)
        await message.answer(
            f"💀 <b>ɢᴀᴍᴇ ᴏᴠᴇʀ</b>\n\nᴛʜᴇ ᴡᴏʀᴅ ᴡᴀs: <b>{word.upper()}</b>"
        )
        return

    # Continue
    await update_word_game(
        message.from_user.id, attempts, "active",
        json.dumps(guesses)
    )
    history = [render_guess(g["word"], g["colors"]) for g in guesses]
    text = game_status_text(length, attempts, max_a, history)
    await message.answer(text, reply_markup=word_game_kb())
