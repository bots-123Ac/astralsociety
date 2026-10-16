"""
handlers/clone.py — Clone bot creation flow.

Every /clone call does a LIVE membership verification. Nothing is
cached as "verified" between clicks.
"""

import logging

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import MAX_TOTAL_CLONES
from utils import clone_db
from utils.bot_context import get_bot_context, is_clone
from utils.clone_manager import start_clone, stop_clone

router = Router()
log = logging.getLogger(__name__)


class CloneFSM(StatesGroup):
    waiting_token = State()


# ═══════════════════════════════════════════════
# LIVE MEMBERSHIP CHECK
# ═══════════════════════════════════════════════
async def _check_all_joined(bot: Bot, user_id: int):
    """
    Live check — always calls Telegram API. No shortcuts.

    Returns (all_joined: bool, missing_records: list, no_required: bool)
    """
    required = await clone_db.get_all_required_chats()

    if not required:
        log.warning(
            f"⚠️ No required chats configured. Clone verification "
            f"impossible for user {user_id}."
        )
        return False, [], True

    missing = []
    for chat in required:
        try:
            member = await bot.get_chat_member(chat["chat_id"], user_id)
            status = member.status
            log.info(
                f"🔎 Membership check: user={user_id} chat={chat['chat_id']} "
                f"status={status}"
            )
            if status in ("left", "kicked"):
                missing.append(chat)
        except Exception as e:
            log.warning(
                f"⚠️ get_chat_member failed for chat {chat['chat_id']} "
                f"user {user_id}: {e}"
            )
            # Treat as missing (safe default)
            missing.append(chat)

    all_joined = len(missing) == 0
    try:
        await clone_db.save_join_cache(
            user_id, all_joined, [c["chat_id"] for c in missing]
        )
    except Exception:
        pass

    return all_joined, missing, False


def _required_join_kb(missing: list) -> InlineKeyboardMarkup:
    rows = []
    for chat in missing:
        label = chat["chat_title"] or str(chat["chat_id"])
        if chat["chat_username"]:
            url = f"https://t.me/{chat['chat_username'].lstrip('@')}"
        elif chat["invite_link"]:
            url = chat["invite_link"]
        else:
            bare = str(chat["chat_id"]).replace("-100", "")
            url = f"https://t.me/c/{bare}"

        prefix = "📢" if chat["chat_type"] == "channel" else "👥"
        rows.append([InlineKeyboardButton(text=f"{prefix} {label}", url=url)])

    rows.append([
        InlineKeyboardButton(text="✅ ᴠᴇʀɪꜰʏ", callback_data="clone:verify"),
    ])
    rows.append([
        InlineKeyboardButton(text="↩️ ʙᴀᴄᴋ", callback_data="menu:main"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _token_instructions() -> str:
    return (
        "🎯 <b>ᴄʟᴏɴᴇ ʙᴏᴛ ꜱᴇᴛᴜᴘ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "<b>ʜᴏᴡ ᴛᴏ ᴄʀᴇᴀᴛᴇ ʏᴏᴜʀ ᴄʟᴏɴᴇ ʙᴏᴛ:</b>\n\n"
        "1️⃣ ɢᴏ ᴛᴏ @BotFather ᴏɴ ᴛᴇʟᴇɢʀᴀᴍ\n"
        "2️⃣ ᴜꜱᴇ /newbot ᴀɴᴅ ꜰᴏʟʟᴏᴡ ᴛʜᴇ ᴘʀᴏᴍᴘᴛꜱ\n"
        "3️⃣ ꜱᴇᴛ ʏᴏᴜʀ ʙᴏᴛ'ꜱ ɴᴀᴍᴇ ᴀɴᴅ ᴜꜱᴇʀɴᴀᴍᴇ\n"
        "4️⃣ ᴄᴏᴘʏ ᴛʜᴇ <b>ᴛᴏᴋᴇɴ</b> ʙᴏᴛꜰᴀᴛʜᴇʀ ɢɪᴠᴇꜱ ʏᴏᴜ\n"
        "5️⃣ ꜱᴇɴᴅ ᴛʜᴀᴛ ᴛᴏᴋᴇɴ ʜᴇʀᴇ 👇\n\n"
        "⚠️ ᴛʜᴇ ᴛᴏᴋᴇɴ ɪꜱ <b>ᴇɴᴄʀʏᴘᴛᴇᴅ</b> ᴀɴᴅ ꜱᴛᴏʀᴇᴅ ꜱᴀꜰᴇʟʏ."
    )


# ═══════════════════════════════════════════════
# SHARED FLOW
# ═══════════════════════════════════════════════
async def _start_clone_flow(
    *, target_msg: Message, bot: Bot, state: FSMContext,
    user_id: int, is_cb: bool = False, cb: CallbackQuery = None,
):
    # Block if called from within a clone bot
    if is_clone():
        text = (
            "🚫 <b>ᴛʜɪꜱ ɪꜱ ᴀ ᴄʟᴏɴᴇ ʙᴏᴛ.</b>\n\n"
            "ᴛᴏ ᴄʀᴇᴀᴛᴇ ʏᴏᴜʀ ᴏᴡɴ ᴄʟᴏɴᴇ, ᴠɪꜱɪᴛ ᴛʜᴇ ᴏʀɪɢɪɴᴀʟ ʙᴏᴛ."
        )
        if is_cb:
            await cb.answer("🚫 ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ ɪɴ ᴄʟᴏɴᴇ", show_alert=True)
        else:
            await target_msg.answer(text)
        return

    # ── Existing clone? ──
    existing = await clone_db.get_clone_by_owner(user_id)
    if existing:
        status = "✅ ᴀᴄᴛɪᴠᴇ" if existing["is_active"] else "🚫 ɪɴᴀᴄᴛɪᴠᴇ"
        text = (
            "🎯 <b>ʏᴏᴜ ᴀʟʀᴇᴀᴅʏ ʜᴀᴠᴇ ᴀ ᴄʟᴏɴᴇ ʙᴏᴛ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🤖 @{existing['bot_username']}\n"
            f"📛 {existing['bot_name']}\n"
            f"📊 ꜱᴛᴀᴛᴜꜱ: {status}\n\n"
            "ᴜꜱᴇ /myclone ᴛᴏ ᴠɪᴇᴡ ᴅᴇᴛᴀɪʟꜱ.\n"
            "ᴜꜱᴇ /deleteclone ᴛᴏ ᴅᴇʟᴇᴛᴇ ɪᴛ."
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="↩️ ʙᴀᴄᴋ", callback_data="menu:main")],
        ])
        if is_cb:
            try:
                await target_msg.edit_text(text, reply_markup=kb)
            except Exception:
                await bot.send_message(user_id, text, reply_markup=kb)
            await cb.answer()
        else:
            await target_msg.answer(text, reply_markup=kb)
        return

    # ── Global cap ──
    total = await clone_db.get_total_clones_count()
    if total >= MAX_TOTAL_CLONES:
        err = (
            "⚠️ <b>ᴄʟᴏɴᴇ ʟɪᴍɪᴛ ʀᴇᴀᴄʜᴇᴅ</b>\n\n"
            f"ᴛʜᴇ ꜱʏꜱᴛᴇᴍ ɪꜱ ᴀᴛ ᴍᴀx ᴄᴀᴘᴀᴄɪᴛʏ ({MAX_TOTAL_CLONES})."
        )
        if is_cb:
            await cb.answer(err, show_alert=True)
        else:
            await target_msg.answer(err)
        return

    # ── LIVE membership check ──
    all_joined, missing, no_required = await _check_all_joined(bot, user_id)

    if no_required:
        err = (
            "⚙️ <b>ᴄʟᴏɴᴇ ꜱʏꜱᴛᴇᴍ ɴᴏᴛ ʀᴇᴀᴅʏ</b>\n\n"
            "ᴛʜᴇ ʙᴏᴛ ᴏᴡɴᴇʀ ʜᴀꜱ ɴᴏᴛ ᴄᴏɴꜰɪɢᴜʀᴇᴅ ᴀɴʏ ʀᴇQᴜɪʀᴇᴅ\n"
            "ᴄʜᴀɴɴᴇʟꜱ ᴏʀ ɢʀᴏᴜᴘꜱ ʏᴇᴛ.\n\n"
            "ᴘʟᴇᴀꜱᴇ ᴄᴏɴᴛᴀᴄᴛ ᴛʜᴇ ʙᴏᴛ ᴏᴡɴᴇʀ."
        )
        if is_cb:
            await cb.answer("⚙️ ɴᴏ ʀᴇQᴜɪʀᴇᴅ ᴄʜᴀᴛꜱ ꜱᴇᴛ", show_alert=True)
        else:
            await target_msg.answer(err)
        return

    if not all_joined:
        text = (
            "📢 <b>ᴊᴏɪɴ ʀᴇQᴜɪʀᴇᴅ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "ᴛᴏ ᴄʀᴇᴀᴛᴇ ʏᴏᴜʀ ᴄʟᴏɴᴇ ʙᴏᴛ, ʏᴏᴜ ᴍᴜꜱᴛ ᴊᴏɪɴ\n"
            "ᴛʜᴇ ꜰᴏʟʟᴏᴡɪɴɢ ᴄʜᴀɴɴᴇʟꜱ/ɢʀᴏᴜᴘꜱ:\n\n"
            "👉 ᴊᴏɪɴ ᴛʜᴇᴍ ᴀʟʟ, ᴛʜᴇɴ ᴛᴀᴘ ᴠᴇʀɪꜰʏ."
        )
        kb = _required_join_kb(missing)
        if is_cb:
            try:
                await target_msg.edit_text(text, reply_markup=kb)
            except Exception:
                await bot.send_message(user_id, text, reply_markup=kb)
            await cb.answer()
        else:
            await target_msg.answer(text, reply_markup=kb)
        return

    # ── Ask for token ──
    await state.set_state(CloneFSM.waiting_token)
    text = _token_instructions()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ ᴄᴀɴᴄᴇʟ", callback_data="clone:cancel")],
    ])
    if is_cb:
        try:
            await target_msg.edit_text(
                text, reply_markup=kb, disable_web_page_preview=True
            )
        except Exception:
            await bot.send_message(
                user_id, text, reply_markup=kb, disable_web_page_preview=True
            )
        await cb.answer()
    else:
        await target_msg.answer(
            text, reply_markup=kb, disable_web_page_preview=True
        )


# ═══════════════════════════════════════════════
# ENTRY POINTS
# ═══════════════════════════════════════════════
@router.message(Command("clone"))
async def cmd_clone(message: Message, state: FSMContext):
    await _start_clone_flow(
        target_msg=message, bot=message.bot, state=state,
        user_id=message.from_user.id,
    )


@router.callback_query(F.data == "clone:start")
async def cb_clone_start(cb: CallbackQuery, state: FSMContext):
    await _start_clone_flow(
        target_msg=cb.message, bot=cb.bot, state=state,
        user_id=cb.from_user.id, is_cb=True, cb=cb,
    )


@router.callback_query(F.data == "clone:verify")
async def cb_clone_verify(cb: CallbackQuery, state: FSMContext):
    await _start_clone_flow(
        target_msg=cb.message, bot=cb.bot, state=state,
        user_id=cb.from_user.id, is_cb=True, cb=cb,
    )


@router.callback_query(F.data == "clone:cancel")
async def cb_clone_cancel(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await cb.message.edit_text("❌ <b>ᴄʟᴏɴᴇ ꜱᴇᴛᴜᴘ ᴄᴀɴᴄᴇʟʟᴇᴅ.</b>")
    except Exception:
        await cb.message.answer("❌ ᴄᴀɴᴄᴇʟʟᴇᴅ.")
    await cb.answer()


# ═══════════════════════════════════════════════
# TOKEN INPUT HANDLER
# ═══════════════════════════════════════════════
@router.message(CloneFSM.waiting_token)
async def process_token(message: Message, state: FSMContext):
    token = (message.text or "").strip()

    if ":" not in token or len(token) < 30 or len(token) > 100:
        return await message.reply(
            "❌ <b>ɪɴᴠᴀʟɪᴅ ᴛᴏᴋᴇɴ ꜰᴏʀᴍᴀᴛ.</b>\n\n"
            "ᴜꜱᴇ /clone ᴛᴏ ʀᴇꜱᴛᴀʀᴛ."
        )

    test_bot = None
    me = None
    try:
        test_bot = Bot(
            token=token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        me = await test_bot.get_me()
    except Exception as e:
        if test_bot:
            try:
                await test_bot.session.close()
            except Exception:
                pass
        return await message.reply(
            "❌ <b>ᴛᴏᴋᴇɴ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ꜰᴀɪʟᴇᴅ</b>\n\n"
            f"ᴇʀʀᴏʀ: <code>{str(e)[:120]}</code>"
        )
    finally:
        if test_bot:
            try:
                await test_bot.session.close()
            except Exception:
                pass

    if await clone_db.token_already_used(me.id):
        return await message.reply(
            "❌ <b>ᴛʜɪꜱ ʙᴏᴛ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴀ ᴄʟᴏɴᴇ.</b>"
        )

    # Re-check membership (still live)
    all_joined, missing, _ = await _check_all_joined(
        message.bot, message.from_user.id
    )
    if not all_joined:
        await state.clear()
        return await message.reply(
            "📢 <b>ʏᴏᴜ ʟᴇꜰᴛ ᴀ ʀᴇQᴜɪʀᴇᴅ ᴄʜᴀᴛ.</b>\n\n"
            "ᴘʟᴇᴀꜱᴇ ʀᴇᴊᴏɪɴ ᴀɴᴅ ᴛʀʏ /clone ᴀɢᴀɪɴ.",
            reply_markup=_required_join_kb(missing),
        )

    try:
        clone_id = await clone_db.create_clone(
            owner_user_id=message.from_user.id,
            owner_username=message.from_user.username,
            owner_first_name=message.from_user.first_name,
            bot_token=token,
            bot_username=me.username or "",
            bot_name=me.full_name or "",
            bot_id=me.id,
        )
    except Exception as e:
        return await message.reply(
            "❌ <b>ᴅᴀᴛᴀʙᴀꜱᴇ ᴇʀʀᴏʀ</b>\n\n"
            f"<code>{str(e)[:200]}</code>"
        )

    rec = await clone_db.get_clone_by_owner(message.from_user.id)
    ok = await start_clone(rec) if rec else False

    await state.clear()

    if not ok:
        await clone_db.delete_clone(clone_id)
        return await message.reply(
            "❌ <b>ᴄʟᴏɴᴇ ꜱᴛᴀʀᴛ ꜰᴀɪʟᴇᴅ.</b>\n\n"
            "ᴛʜᴇ ʙᴏᴛ ᴄᴏᴜʟᴅ ɴᴏᴛ ʙᴇ ꜱᴛᴀʀᴛᴇᴅ (token ɪɴᴠᴀʟɪᴅ)."
        )

    await message.reply(
        "🎉 <b>ᴄʟᴏɴᴇ ʙᴏᴛ ᴄʀᴇᴀᴛᴇᴅ!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🤖 <b>@{me.username}</b>\n"
        f"📛 {me.full_name}\n\n"
        "✅ ʏᴏᴜ ᴀʀᴇ ᴛʜᴇ ᴏᴡɴᴇʀ ᴏꜰ ᴛʜɪꜱ ʙᴏᴛ.\n"
        "🚀 ɪᴛ'ꜱ ɴᴏᴡ ʀᴜɴɴɪɴɢ ʟɪᴠᴇ!\n\n"
        f"👉 ᴏᴘᴇɴ ɪᴛ: https://t.me/{me.username}",
        disable_web_page_preview=True,
    )


# ═══════════════════════════════════════════════
# /myclone
# ═══════════════════════════════════════════════
@router.message(Command("myclone"))
async def cmd_myclone(message: Message):
    clone = await clone_db.get_clone_by_owner(message.from_user.id)
    if not clone:
        return await message.reply(
            "❌ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀ ᴄʟᴏɴᴇ ʙᴏᴛ ʏᴇᴛ.\n\nᴜꜱᴇ /clone ᴛᴏ ᴄʀᴇᴀᴛᴇ ᴏɴᴇ!"
        )

    status = "✅ ᴀᴄᴛɪᴠᴇ" if clone["is_active"] else "🚫 ɪɴᴀᴄᴛɪᴠᴇ"
    err_line = (
        f"\n⚠️ ʟᴀꜱᴛ ᴇʀʀᴏʀ: <code>{clone['last_error'][:120]}</code>"
        if clone["last_error"] else ""
    )

    await message.reply(
        "🤖 <b>ʏᴏᴜʀ ᴄʟᴏɴᴇ ʙᴏᴛ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📛 ɴᴀᴍᴇ: <b>{clone['bot_name']}</b>\n"
        f"🆔 ᴜꜱᴇʀɴᴀᴍᴇ: @{clone['bot_username']}\n"
        f"📊 ꜱᴛᴀᴛᴜꜱ: {status}\n"
        f"📅 ᴄʀᴇᴀᴛᴇᴅ: {clone['created_at']}"
        f"{err_line}"
    )


# ═══════════════════════════════════════════════
# /deleteclone
# ═══════════════════════════════════════════════
@router.message(Command("deleteclone"))
async def cmd_deleteclone(message: Message):
    clone = await clone_db.get_clone_by_owner(message.from_user.id)
    if not clone:
        return await message.reply("❌ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀ ᴄʟᴏɴᴇ ʙᴏᴛ.")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🗑️ ʏᴇꜱ, ᴅᴇʟᴇᴛᴇ",
                callback_data="clone:confirm_delete",
            ),
            InlineKeyboardButton(text="❌ ᴄᴀɴᴄᴇʟ", callback_data="menu:main"),
        ],
    ])
    await message.reply(
        "⚠️ <b>ᴅᴇʟᴇᴛᴇ ᴄʟᴏɴᴇ?</b>\n\n"
        f"🤖 @{clone['bot_username']}\n\n"
        "ᴛʜɪꜱ ᴡɪʟʟ ʀᴇᴍᴏᴠᴇ ʏᴏᴜʀ ᴄʟᴏɴᴇ ꜰʀᴏᴍ ᴛʜᴇ ꜱʏꜱᴛᴇᴍ.",
        reply_markup=kb,
    )


@router.callback_query(F.data == "clone:confirm_delete")
async def cb_confirm_delete(cb: CallbackQuery):
    clone = await clone_db.get_clone_by_owner(cb.from_user.id)
    if not clone:
        return await cb.answer("❌ ɴᴏ ᴄʟᴏɴᴇ ꜰᴏᴜɴᴅ.", show_alert=True)

    try:
        await stop_clone(clone["id"])
    except Exception:
        pass

    await clone_db.delete_clone(clone["id"])

    try:
        await cb.message.edit_text(
            "✅ <b>ᴄʟᴏɴᴇ ʙᴏᴛ ᴅᴇʟᴇᴛᴇᴅ.</b>"
        )
    except Exception:
        await cb.message.answer("✅ ᴄʟᴏɴᴇ ᴅᴇʟᴇᴛᴇᴅ.")
    await cb.answer("✅ ᴅᴇʟᴇᴛᴇᴅ")
