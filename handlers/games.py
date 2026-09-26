import random
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.games_kb import (
    games_main_kb, fortune_kb, arena_kb, beast_kb,
    detective_kb, raid_kb, game_lb_menu_kb,
)
from keyboards.main_menu import back_kb
from utils.database import (
    get_balance, add_coins, add_points, save_game_score, get_leaderboard,
)
from utils.ui import smart_edit

router = Router()


class ArenaFlow(StatesGroup):
    active = State()


# ─────────────────────────────────────────────
# MAIN GAMES MENU
# ─────────────────────────────────────────────
@router.callback_query(F.data == "menu:games")
async def show_games(cb: CallbackQuery):
    text = (
        "🎮 <b>ɢᴧϻєs sєᴄᴛiση</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "ᴄнσσsє ᴧ ɢᴧϻє тσ ᴩʟᴧʏ:\n\n"
        "єᴧᴄн ɢᴧϻє нᴧs its σᴡη єᴄσησϻʏ, "
        "ᴜᴩɢʀᴧᴅєs & ʟєᴧᴅєʀвσᴧʀᴅ."
    )
    await smart_edit(cb, text, games_main_kb())
    await cb.answer()


# ─────────────────────────────────────────────
# 🎰 FORTUNE
# ─────────────────────────────────────────────
@router.callback_query(F.data == "game:fortune")
async def fortune_menu(cb: CallbackQuery):
    bal = await get_balance(cb.from_user.id)
    coins = bal[0] if bal else 0
    text = (
        "🎰 <b>ᴧsᴛʀᴧʟ ғσʀᴛᴜηє</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 ʏσᴜʀ ᴄσiηs: <b>{coins}</b>\n\n"
        "🎲 ʀσʟʟ тнє ᴅiᴄє — iғ ʏσᴜ ɢєᴛ 4, 5, σʀ 6, ʏσᴜ ᴅσᴜвʟє!\n\n"
        "ᴄнσσsє ʙєᴛ:"
    )
    await smart_edit(cb, text, fortune_kb())
    await cb.answer()


@router.callback_query(F.data.startswith("fortune:bet:"))
async def fortune_play(cb: CallbackQuery):
    bet = int(cb.data.split(":")[2])
    bal = await get_balance(cb.from_user.id)
    coins = bal[0] if bal else 0

    if coins < bet:
        await cb.answer(f"❌ ɴᴏᴛ єɴᴏᴜɢʜ ᴄᴏɪɴs! ʏᴏᴜ ʜᴀᴠᴇ {coins}", show_alert=True)
        return

    roll = random.randint(1, 6)
    if roll >= 4:
        winnings = bet * 2
        await add_coins(cb.from_user.id, winnings - bet)
        await add_points(cb.from_user.id, 5)
        await save_game_score(cb.from_user.id, "fortune", winnings)
        result = f"🎉 ʏᴏᴜ ʀᴏʟʟᴇᴅ <b>{roll}</b>!\n💰 ʏᴏᴜ ᴡᴏɴ <b>{winnings} ᴄᴏɪɴs</b>!"
    else:
        await add_coins(cb.from_user.id, -bet)
        await save_game_score(cb.from_user.id, "fortune", 0)
        result = f"😢 ʏᴏᴜ ʀᴏʟʟᴇᴅ <b>{roll}</b>.\n💸 ʏᴏᴜ ʟᴏsᴛ <b>{bet} ᴄᴏɪɴs</b>."

    new_bal = await get_balance(cb.from_user.id)
    text = (
        "🎰 <b>ᴧsᴛʀᴧʟ ғσʀᴛᴜηє</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{result}\n\n"
        f"💰 ηєᴡ ʙᴧʟᴧηᴄє: <b>{new_bal[0]}</b> ᴄσiηs\n\n"
        "ᴡᴧηηᴧ ᴩʟᴧʏ ᴧɢᴧiη?"
    )
    await smart_edit(cb, text, fortune_kb())
    await cb.answer()


# ─────────────────────────────────────────────
# ⚔️ ARENA
# ─────────────────────────────────────────────
@router.callback_query(F.data == "game:arena")
async def arena_menu(cb: CallbackQuery, state: FSMContext):
    await state.update_data(player_hp=100, bot_hp=100)
    text = (
        "⚔️ <b>ᴧsᴛʀᴧʟ ᴧʀєηᴧ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "👤 ʏσᴜ:  ██████████ 100 нᴩ\ n"
        "🤖 вσᴛ:  ██████████ 100 нᴩ\n\n"
        "ᴄнσσsє ʏσᴜʀ ᴧᴄᴛiση:"
    ).replace("\\ n", "\n")
    await smart_edit(cb, text, arena_kb())
    await cb.answer()


@router.callback_query(F.data == "arena:attack")
async def arena_attack(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data:
        await cb.answer("sᴛᴧʀᴛ ᴧ ɴєᴡ вᴧᴛᴛʟє", show_alert=True)
        return

    bot_hp = data.get("bot_hp", 100)
    player_hp = data.get("player_hp", 100)

    player_dmg = random.randint(15, 30)
    bot_hp -= player_dmg

    if bot_hp <= 0:
        reward = 100
        await add_coins(cb.from_user.id, reward)
        await add_points(cb.from_user.id, 10)
        await save_game_score(cb.from_user.id, "arena", 100)
        await state.clear()
        text = (
            "⚔️ <b>ᴧsᴛʀᴧʟ ᴧʀєηᴧ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🗡️ ʏᴏᴜ ᴅєᴧʟᴛ <b>{player_dmg}</b> ᴅᴧϻᴧɢє!\n"
            f"🤖 вσᴛ ᴅєғєᴧᴛєᴅ!\n\n"
            f"🎉 <b>ᴠiᴄᴛσʀʏ!</b>\n"
            f"💰 +{reward} ᴄσiηs | ⭐ +10 ᴩσiηᴛs"
        )
        await smart_edit(cb, text, arena_kb())
        await cb.answer("🎉 ᴠɪᴄᴛᴏʀʏ!")
        return

    bot_dmg = random.randint(10, 25)
    player_hp -= bot_dmg

    if player_hp <= 0:
        await save_game_score(cb.from_user.id, "arena", 0)
        await state.clear()
        text = (
            "⚔️ <b>ᴧsᴛʀᴧʟ ᴧʀєηᴧ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🗡️ ʏᴏᴜ ᴅєᴧʟᴛ <b>{player_dmg}</b>\n"
            f"🤖 вσᴛ ᴅєᴧʟᴛ <b>{bot_dmg}</b>\n\n"
            f"💀 <b>ᴅєғєᴧᴛ!</b>"
        )
        await smart_edit(cb, text, arena_kb())
        await cb.answer("💀 ʏᴏᴜ ʟᴏsᴛ!")
        return

    await state.update_data(player_hp=player_hp, bot_hp=bot_hp)

    p_bar = "█" * (player_hp // 10) + "░" * (10 - player_hp // 10)
    b_bar = "█" * (bot_hp // 10) + "░" * (10 - bot_hp // 10)

    text = (
        "⚔️ <b>ᴧsᴛʀᴧʟ ᴧʀєηᴧ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 ʏσᴜ:  {p_bar} {player_hp} нᴩ\ n"
        f"🤖 вσᴛ:  {b_bar} {bot_hp} нᴩ\n\n"
        f"🗡️ ʏᴏᴜ ᴅєᴧʟᴛ <b>{player_dmg}</b> | 🤖 вσᴛ ᴅєᴧʟᴛ <b>{bot_dmg}</b>\n\n"
        "ᴄнσσsє ʏσᴜʀ ᴧᴄᴛiση:"
    ).replace("\\ n", "\n")
    await smart_edit(cb, text, arena_kb())
    await cb.answer()


@router.callback_query(F.data == "arena:defend")
async def arena_defend(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data:
        await cb.answer("sᴛᴧʀᴛ ᴧ ɴєᴡ вᴧᴛᴛʟє", show_alert=True)
        return
    bot_hp = data.get("bot_hp", 100)
    player_hp = data.get("player_hp", 100)
    bot_dmg = random.randint(5, 10)
    player_hp -= bot_dmg
    await state.update_data(player_hp=player_hp, bot_hp=bot_hp)

    p_bar = "█" * (max(player_hp, 0) // 10) + "░" * (10 - max(player_hp, 0) // 10)
    b_bar = "█" * (bot_hp // 10) + "░" * (10 - bot_hp // 10)

    text = (
        "⚔️ <b>ᴧsᴛʀᴧʟ ᴧʀєηᴧ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 ʏσᴜ:  {p_bar} {max(player_hp, 0)} нᴩ\ n"
        f"🤖 вσᴛ:  {b_bar} {bot_hp} нᴩ\n\n"
        f"🛡️ ʏᴏᴜ ᴅєғєηᴅєᴅ! 🤖 вσᴛ ᴅєᴧʟᴛ <b>{bot_dmg}</b>\n\n"
        "ᴄнσσsє ʏσᴜʀ ᴧᴄᴛiση:"
    ).replace("\\ n", "\n")
    await smart_edit(cb, text, arena_kb())
    await cb.answer()


# ─────────────────────────────────────────────
# 🐉 BEAST
# ─────────────────────────────────────────────
@router.callback_query(F.data == "game:beast")
async def beast_menu(cb: CallbackQuery):
    text = (
        "🐉 <b>ᴧsᴛʀᴧʟ вєᴧsᴛ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "ʏσᴜʀ вєᴧsᴛ: <b>ᴅʀᴧᴋσ</b>\n"
        "ʟєᴠєʟ: 1 | xᴩ: 0/100\n\n"
        "ғєєᴅ (10 ᴄσiηs) → +20 xᴩ\n"
        "ᴛʀᴧiη (20 ᴄσiηs) → +30 xᴩ"
    )
    await smart_edit(cb, text, beast_kb())
    await cb.answer()


@router.callback_query(F.data.startswith("beast:"))
async def beast_action(cb: CallbackQuery):
    action = cb.data.split(":")[1]
    cost = 10 if action == "feed" else 20
    xp = 20 if action == "feed" else 30
    bal = await get_balance(cb.from_user.id)
    coins = bal[0] if bal else 0
    if coins < cost:
        await cb.answer(f"❌ ɴᴏᴛ єɴᴏᴜɢʜ ᴄᴏɪɴs! (ηєєᴅ {cost})", show_alert=True)
        return
    await add_coins(cb.from_user.id, -cost)
    await add_points(cb.from_user.id, 2)
    await save_game_score(cb.from_user.id, "beast", xp)
    new_bal = await get_balance(cb.from_user.id)
    text = (
        "🐉 <b>ᴧsᴛʀᴧʟ вєᴧsᴛ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"✅ ʏσᴜʀ вєᴧsᴛ ɢᴧiηєᴅ <b>+{xp} xᴩ</b>!\n\n"
        f"💰 ʙᴧʟᴧηᴄє: <b>{new_bal[0]}</b> ᴄσiηs"
    )
    await smart_edit(cb, text, beast_kb())
    await cb.answer()


# ─────────────────────────────────────────────
# 🧩 DETECTIVE
# ─────────────────────────────────────────────
RIDDLES = [
    ("i sᴩєᴧᴋ ᴡiᴛнσᴜᴛ ᴧ ϻσᴜᴛн, i нєᴧʀ ᴡiᴛнσᴜᴛ єᴧʀs. i нᴧᴠє ησ вσᴅʏ, вᴜᴛ i ᴄσϻє ᴧʟiᴠє ᴡiᴛн ᴡiηᴅ. ᴡнᴧᴛ ᴧϻ i?", "echo"),
    ("тнє ϻσʀє ʏσᴜ тᴧᴋє, тнє ϻσʀє ʏσᴜ ʟєᴧᴠє вєнiηᴅ. ᴡнᴧᴛ ᴧϻ i?", "footsteps"),
    ("i нᴧᴠє нᴧηᴅs ᴜᴛ ησ ғєєт, i нᴧᴠє ᴧ ғᴧᴄє вᴜᴛ ησ ϻσᴜᴛн. ᴡнᴧᴛ ᴧϻ i?", "clock"),
]


@router.callback_query(F.data == "game:detective")
async def detective_menu(cb: CallbackQuery):
    riddle, _ = random.choice(RIDDLES)
    text = (
        f"🧩 <b>ᴧsᴛʀᴧʟ ᴅєᴛєᴄᴛiᴠє</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ᴛσᴅᴧʏ's ʀiᴅᴅʟє:\n\n<i>{riddle}</i>\n\n"
        f"ᴛʏᴩє ʏσᴜʀ ᴧηsᴡєʀ iη ᴄнᴧᴛ!"
    )
    await smart_edit(cb, text, detective_kb())
    await cb.answer()


@router.callback_query(F.data == "detective:investigate")
async def detective_investigate(cb: CallbackQuery):
    await add_coins(cb.from_user.id, 5)
    await add_points(cb.from_user.id, 3)
    await save_game_score(cb.from_user.id, "detective", 5)
    await cb.answer("🔍 iηνєsᴛiɢᴧᴛiση ᴄσϻᴩʟєᴛє! +5 ᴄσiηs, +3 ᴩσiηᴛs", show_alert=True)


# ─────────────────────────────────────────────
# 🏹 RAID
# ─────────────────────────────────────────────
@router.callback_query(F.data == "game:raid")
async def raid_menu(cb: CallbackQuery):
    text = (
        "🏹 <b>ᴧsᴛʀᴧʟ ʀᴧiᴅ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🐲 ʙσss: ᴅʀᴧɢση\n"
        "нᴩ: ██████████ 100/100\n\n"
        "ᴧᴛᴛᴧᴄᴋ тнє вσss!"
    )
    await smart_edit(cb, text, raid_kb())
    await cb.answer()


@router.callback_query(F.data == "raid:attack")
async def raid_attack(cb: CallbackQuery):
    dmg = random.randint(10, 25)
    reward = dmg
    await add_coins(cb.from_user.id, reward)
    await add_points(cb.from_user.id, 5)
    await save_game_score(cb.from_user.id, "raid", dmg)
    text = (
        "🏹 <b>ᴧsᴛʀᴧʟ ʀᴧiᴅ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⚔️ ʏσᴜ ᴅєᴧʟᴛ <b>{dmg}</b> ᴅᴧϻᴧɢє!\n"
        f"💰 +{reward} ᴄσiηs | ⭐ +5 ᴩσiηᴛs"
    )
    await smart_edit(cb, text, raid_kb())
    await cb.answer("⚔️ нiᴛ!")


# ─────────────────────────────────────────────
# 🏆 LEADERBOARDS (Per Game)
# ─────────────────────────────────────────────
@router.callback_query(F.data == "game:lb_menu")
async def lb_menu(cb: CallbackQuery):
    text = "🏆 <b>ɢᴧϻє ʟєᴧᴅєʀвσᴧʀᴅ</b>\n━━━━━━━━━━━━━━━━━━━━━\n\nᴄнσσsє ᴧ ɢᴧϻє:"
    await smart_edit(cb, text, game_lb_menu_kb())
    await cb.answer()


@router.callback_query(F.data.startswith("lb:"))
async def show_game_lb(cb: CallbackQuery):
    game = cb.data.split(":")[1]
    rows = await get_leaderboard(game, 10)
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

    if not rows:
        body = "ησ sᴄσʀєs ʏєᴛ. вє тнє ғiʀsᴛ!"
    else:
        body = "\n".join(
            f"{medals[i]} {name} — <b>{score}</b>"
            for i, (name, uname, score) in enumerate(rows)
        )

    text = (
        f"🏆 <b>{game.upper()} ʟєᴧᴅєʀвσᴧʀᴅ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n{body}"
    )
    await smart_edit(cb, text, game_lb_menu_kb())
    await cb.answer()
