import json
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext

from keyboards.main_menu import back_kb
from utils.database import (
    start_word_game, get_word_game, update_word_game, end_word_game,
    end_all_games_in_chat, get_active_games_in_chat,
    add_points, add_coins, get_word_leaderboard,
)
from utils.words import get_random_word, words_count
from utils.permissions import has_right
from utils.ui import smart_edit

router = Router()

MAX_ATTEMPTS = 30


# ═══════════════════════════════════════════════
# KEYBOARDS (self-contained)
# ═══════════════════════════════════════════════
def games_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔤 ᴡᴏʀᴅ ɢᴜᴇssɪɴɢ", callback_data="wg:menu")],
        [InlineKeyboardButton(text="↩️ вᴀᴄᴋ", callback_data="menu:main")],
    ])


def word_length_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="4️⃣ 4 ʟᴇᴛᴛᴇʀs", callback_data="wg:new:4"),
         InlineKeyboardButton(text="5️⃣ 5 ʟᴇᴛᴛᴇʀs", callback_data="wg:new:5")],
        [InlineKeyboardButton(text="6️⃣ 6 ʟᴇᴛᴛᴇʀs", callback_data="wg:new:6")],
        [InlineKeyboardButton(text="↩️ вᴀᴄᴋ", callback_data="menu:games")],
    ])


def word_game_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 sᴛᴀᴛᴜs", callback_data="wg:status"),
         InlineKeyboardButton(text="🛑 ɢɪᴠᴇ ᴜᴘ", callback_data="wg:giveup")],
    ])


def leaderboard_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔤 ᴡᴏʀᴅ ɢᴀᴍᴇ", callback_data="lb:word")],
        [InlineKeyboardButton(text="📝 ǫᴜɪᴢ", callback_data="lb:quiz")],
        [InlineKeyboardButton(text="↩️ вᴀᴄᴋ", callback_data="menu:main")],
    ])


# ═══════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════
def score_for_attempt(attempts: int, length: int) -> int:
    base = {4: 200, 5: 300, 6: 400}.get(length, 300)
    if attempts <= 1:
        return base
    return max(10, base // attempts)


def evaluate_guess(word: str, guess: str) -> list:
    result = ["grey"] * len(word)
    wc = list(word); gc = list(guess)
    for i in range(len(word)):
        if gc[i] == wc[i]:
            result[i] = "green"; wc[i] = None; gc[i] = None
    for i in range(len(word)):
        if gc[i] and gc[i] in wc:
            result[i] = "yellow"; wc[wc.index(gc[i])] = None
    return result


def render_guess(guess: str, colors: list) -> str:
    emoji = {"green": "🟩", "yellow": "🟨", "grey": "⬛"}
    chars = " ".join(c.upper() for c in guess)
    boxes = " ".join(emoji[c] for c in colors)
    return f"<code>{chars}</code>\n{boxes}"


def status_text(length, attempts, max_a, history, mention=None):
    head = f"🔤 <b>ᴡᴏʀᴅ ɢᴜᴇssɪɴɢ</b>"
    if mention:
        head += f" — {mention}"
    return (
        f"{head}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📏 ʟᴇɴɢᴛʜ: <b>{length}</b> ʟᴇᴛᴛᴇʀs\n"
        f"🎯 ᴀᴛᴛᴇᴍᴘᴛs: <b>{attempts}/{max_a}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{chr(10).join(history)}\n\n"
        f"ᴛʏᴘᴇ ʏᴏᴜʀ ɢᴜᴇss ({length} ʟᴇᴛᴛᴇʀs):"
    )


# ═══════════════════════════════════════════════
# MENUS
# ═══════════════════════════════════════════════
@router.callback_query(F.data == "menu:games")
async def games_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    text = (
        "🎮 <b>ɢᴀᴍᴇs</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "ᴄʜᴏᴏsᴇ ᴀ ɢᴀᴍᴇ:\n\n"
        "🔤 ᴡᴏʀᴅ ɢᴜᴇssɪɴɢ — ᴅᴍ & ɢʀᴏᴜᴘ"
    )
    await smart_edit(cb, text, games_menu_kb())
    await cb.answer()


@router.callback_query(F.data == "wg:menu")
async def wg_menu(cb: CallbackQuery, state: FSMContext):
    counts = words_count()
    text = (
        "🔤 <b>ᴡᴏʀᴅ ɢᴜᴇssɪɴɢ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🟩 ᴄᴏʀʀᴇᴄᴛ ʟᴇᴛᴛᴇʀ + ᴘᴏsɪᴛɪᴏɴ\n"
        "🟨 ᴄᴏʀʀᴇᴄᴛ ʟᴇᴛᴛᴇʀ, ᴡʀᴏɴɢ ᴘᴏsɪᴛɪᴏɴ\n"
        "⬛ ʟᴇᴛᴛᴇʀ ɴᴏᴛ ɪɴ ᴡᴏʀᴅ\n\n"
        f"📚 ᴘᴏᴏʟ: 4L={counts.get(4,0)} | 5L={counts.get(5,0)} | 6L={counts.get(6,0)}\n"
        f"🎯 ᴍᴀx ᴀᴛᴛᴇᴍᴘᴛs: {MAX_ATTEMPTS}\n"
        f"⭐ ғᴇᴡᴇʀ ᴀᴛᴛᴇᴍᴘᴛs = ᴍᴏʀᴇ ᴘᴏɪɴᴛs\n\n"
        f"ᴄʜᴏᴏsᴇ ʟᴇɴɢᴛʜ:"
    )
    await smart_edit(cb, text, word_length_kb())
    await cb.answer()


@router.callback_query(F.data.startswith("wg:new:"))
async def wg_new(cb: CallbackQuery, state: FSMContext):
    try:
        length = int(cb.data.split(":")[2])
    except (ValueError, IndexError):
        return await cb.answer("ɪɴᴠᴀʟɪᴅ", show_alert=True)
    if length not in (4, 5, 6):
        return await cb.answer("ɪɴᴠᴀʟɪᴅ", show_alert=True)

    word = get_random_word(length)
    await start_word_game(cb.from_user.id, cb.message.chat.id, word, length)
    text = status_text(length, 0, MAX_ATTEMPTS, ["🎯 sᴛᴀʀᴛ ɢᴜᴇssɪɴɢ!"])
    await smart_edit(cb, text, word_game_kb())
    await cb.answer(f"ɢᴀᴍᴇ sᴛᴀʀᴛᴇᴅ! {length} ʟᴇᴛᴛᴇʀs")


@router.callback_query(F.data == "wg:status")
async def wg_status(cb: CallbackQuery):
    row = await get_word_game(cb.from_user.id, cb.message.chat.id)
    if not row:
        return await cb.answer("ηᴏ ᴀᴄᴛɪᴠᴇ ɢᴀᴍᴇ", show_alert=True)
    word, length, attempts, max_a, status, gj = row
    guesses = json.loads(gj or "[]")
    history = [render_guess(g["word"], g["colors"]) for g in guesses] or ["🎯 sᴛᴀʀᴛ ɢᴜᴇssɪɴɢ!"]
    await smart_edit(cb, status_text(length, attempts, max_a, history), word_game_kb())
    await cb.answer()


@router.callback_query(F.data == "wg:giveup")
async def wg_giveup(cb: CallbackQuery, bot: Bot):
    chat_id = cb.message.chat.id
    # In groups — only admins can force-end; in DM — only self
    if cb.message.chat.type != "private":
        if not await has_right(bot, chat_id, cb.from_user.id, "can_delete_messages"):
            return await cb.answer("❌ ᴀᴅᴍɪɴs ᴏɴʟʏ ɪɴ ɢʀᴏᴜᴘs", show_alert=True)
        # Admin ends all games in group
        await end_all_games_in_chat(chat_id)
        text = f"🛑 <b>ᴀʟʟ ɢᴀᴍᴇs ᴇɴᴅᴇᴅ ʙʏ ᴀᴅᴍɪɴ.</b>"
        await smart_edit(cb, text, games_menu_kb())
        return await cb.answer()

    row = await get_word_game(cb.from_user.id, chat_id)
    if not row:
        return await cb.answer("ηᴏ ᴀᴄᴛɪᴠᴇ ɢᴀᴍᴇ", show_alert=True)
    word, length, attempts, _, _, _ = row
    await end_word_game(cb.from_user.id, chat_id, word, attempts, False, 0)
    text = f"🛑 ᴛʜᴇ ᴡᴏʀᴅ ᴡᴀs: <b>{word.upper()}</b>"
    await smart_edit(cb, text, games_menu_kb())
    await cb.answer()


# ═══════════════════════════════════════════════
# /new COMMAND (DM + Group)
# ═══════════════════════════════════════════════
@router.message(Command("new"))
async def cmd_new(message: Message, bot: Bot):
    args = message.text.split()
    chat_type = message.chat.type

    # In group — /end to end game
    if len(args) >= 2 and args[1].lower() in ("end", "stop"):
        if chat_type == "private":
            return await message.reply("ᴜsᴇ ᴛʜᴇ 🛑 ɢɪᴠᴇ-ᴜᴘ ʙᴜᴛᴛᴏɴ.")
        if not await has_right(bot, message.chat.id, message.from_user.id, "can_delete_messages"):
            return await message.reply("❌ ᴀᴅᴍɪɴs ᴏɴʟʏ.")
        await end_all_games_in_chat(message.chat.id)
        return await message.reply("🛑 ᴀʟʟ ᴀᴄᴛɪᴠᴇ ɢᴀᴍᴇs ᴇɴᴅᴇᴅ.")

    # /new 4 or /new five
    length_map = {"4": 4, "four": 4, "5": 5, "five": 5, "6": 6, "six": 6}
    if len(args) >= 2:
        key = args[1].lower()
        if key in length_map:
            length = length_map[key]
            word = get_random_word(length)
            await start_word_game(message.from_user.id, message.chat.id, word, length)
            text = status_text(length, 0, MAX_ATTEMPTS, ["🎯 sᴛᴀʀᴛ ɢᴜᴇssɪɴɢ!"])
            return await message.answer(text, reply_markup=word_game_kb())

    # No args — show menu
    text = (
        "🔤 <b>ᴡᴏʀᴅ ɢᴜᴇssɪɴɢ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "ᴜsᴀɢᴇ:\n"
        "• /new 4 — 4 ʟᴇᴛᴛᴇʀ ᴡᴏʀᴅ\n"
        "• /new 5 — 5 ʟᴇᴛᴛᴇʀ ᴡᴏʀᴅ\n"
        "• /new 6 — 6 ʟᴇᴛᴛᴇʀ ᴡᴏʀᴅ\n"
        "• /new end — ᴇɴᴅ ɢᴀᴍᴇs (ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs)\n\n"
        "ᴏʀ ᴘɪᴄᴋ ʟᴇɴɢᴛʜ ʙᴇʟᴏᴡ:"
    )
    await message.answer(text, reply_markup=word_length_kb())


# ═══════════════════════════════════════════════
# GUESS HANDLER (DM + Group)
# ═══════════════════════════════════════════════
@router.message(F.text & ~F.text.startswith("/"))
async def handle_guess(message: Message, state: FSMContext):
    if not message.text:
        return

    # Skip command-like or very short
    guess = message.text.strip().lower()
    if not guess.isalpha():
        return

    row = await get_word_game(message.from_user.id, message.chat.id)
    if not row:
        return
    word, length, attempts, max_a, status, gj = row
    if status != "active":
        return

    # Length mismatch — ignore in groups, warn in DM
    if len(guess) != length:
        if message.chat.type == "private":
            await message.answer(f"❌ sᴇɴᴅ ᴀ <b>{length}-ʟᴇᴛᴛᴇʀ</b> ᴡᴏʀᴅ.")
        return

    colors = evaluate_guess(word, guess)
    guesses = json.loads(gj or "[]")
    guesses.append({"word": guess, "colors": colors})
    attempts += 1

    # WIN
    if all(c == "green" for c in colors):
        score = score_for_attempt(attempts, length)
        await end_word_game(message.from_user.id, message.chat.id, word, attempts, True, score)
        await add_points(message.from_user.id, score)
        await add_coins(message.from_user.id, score // 2)
        header = f"🎉 <b>{message.from_user.mention_html()} ᴡᴏɴ!</b>"
        await message.answer(
            f"{header}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"ᴛʜᴇ ᴡᴏʀᴅ ᴡᴀs: <b>{word.upper()}</b>\n"
            f"ᴀᴛᴛᴇᴍᴘᴛs: <b>{attempts}</b>\n\n"
            f"⭐ ᴘᴏɪɴᴛs: <b>+{score}</b>\n"
            f"🪙 ᴄᴏɪɴs: <b>+{score // 2}</b>"
        )
        return

    # LOSS
    if attempts >= max_a:
        await end_word_game(message.from_user.id, message.chat.id, word, attempts, False, 0)
        await message.answer(
            f"💀 <b>{message.from_user.mention_html()} — ɢᴀᴍᴇ ᴏᴠᴇʀ</b>\n"
            f"ᴛʜᴇ ᴡᴏʀᴅ ᴡᴀs: <b>{word.upper()}</b>"
        )
        return

    # CONTINUE
    await update_word_game(
        message.from_user.id, message.chat.id, attempts, "active", json.dumps(guesses)
    )
    history = [render_guess(g["word"], g["colors"]) for g in guesses]
    mention = message.from_user.mention_html() if message.chat.type != "private" else None
    text = status_text(length, attempts, max_a, history, mention=mention)
    await message.answer(text, reply_markup=word_game_kb())


# ═══════════════════════════════════════════════
# LEADERBOARD
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
        body = "ηᴏ sᴄᴏʀᴇs ʏᴇᴛ."
    else:
        body = "\n".join(
            f"{medals[i]} {(f'@{u}' if u else n)} — <b>{s}</b> ᴘᴛs"
            for i, (n, u, s) in enumerate(rows)
        )
    text = f"🏆 <b>ᴡᴏʀᴅ ɢᴀᴍᴇ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n{body}"
    await smart_edit(cb, text, leaderboard_menu_kb())
    await cb.answer()


@router.callback_query(F.data == "lb:quiz")
async def lb_quiz(cb: CallbackQuery):
    text = (
        f"🏆 <b>ǫᴜɪᴢ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ᴜsᴇ /profile ᴛᴏ sᴇᴇ ʏᴏᴜʀ ᴏᴡɴ sᴛᴀᴛs."
    )
    await smart_edit(cb, text, leaderboard_menu_kb())
    await cb.answer()
