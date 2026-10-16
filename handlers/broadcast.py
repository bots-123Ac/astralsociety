"""
handlers/broadcast.py — Owner-only broadcast with auto-cleanup of dead users.
"""

import asyncio
from datetime import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.exceptions import (
    TelegramForbiddenError,
    TelegramBadRequest,
    TelegramRetryAfter,
)

from config import OWNER_IDS
from utils import clone_db
from utils.database import (
    get_dead_users_list, get_all_registered_groups_count,
)

router = Router()

_last_broadcast_stats: dict = {}

MESSAGES_PER_SECOND = 25
DELAY_BETWEEN = 1.0 / MESSAGES_PER_SECOND


def _is_owner(user_id: int) -> bool:
    return user_id in OWNER_IDS


# ═══════════════════════════════════════════════
# ENTRY COMMANDS
# ═══════════════════════════════════════════════
@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message):
    if not _is_owner(message.from_user.id):
        return
    if not message.reply_to_message:
        return await message.reply(
            "📢 <b>ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴜꜱᴀɢᴇ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴍᴇꜱꜱᴀɢᴇ ᴡɪᴛʜ <code>/broadcast</code>\n"
            "ᴛᴏ ꜱᴇɴᴅ ɪᴛ ᴛᴏ ᴀʟʟ ᴜꜱᴇʀꜱ & ɢʀᴏᴜᴘꜱ."
        )
    await _do_broadcast(message, message.reply_to_message, True, True)


@router.message(Command("broadcast_users"))
async def cmd_broadcast_users(message: Message):
    if not _is_owner(message.from_user.id):
        return
    if not message.reply_to_message:
        return await message.reply(
            "ᴜꜱᴀɢᴇ: ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇꜱꜱᴀɢᴇ ᴡɪᴛʜ <code>/broadcast_users</code>"
        )
    await _do_broadcast(message, message.reply_to_message, True, False)


@router.message(Command("broadcast_groups"))
async def cmd_broadcast_groups(message: Message):
    if not _is_owner(message.from_user.id):
        return
    if not message.reply_to_message:
        return await message.reply(
            "ᴜꜱᴀɢᴇ: ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇꜱꜱᴀɢᴇ ᴡɪᴛʜ <code>/broadcast_groups</code>"
        )
    await _do_broadcast(message, message.reply_to_message, False, True)


# ═══════════════════════════════════════════════
# SINGLE SEND WITH RETRY
# ═══════════════════════════════════════════════
async def _send_to(source_msg: Message, chat_id: int):
    """Returns (ok, reason, user_id_to_delete_or_None)."""
    for attempt in range(3):
        try:
            await source_msg.copy_to(chat_id=chat_id)
            return True, "ok", None

        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after + 1)
            continue

        except TelegramForbiddenError:
            return False, "blocked", chat_id

        except TelegramBadRequest as e:
            err = str(e).lower()
            if "chat not found" in err or "user is deactivated" in err:
                return False, "deleted", chat_id
            return False, "other", None

        except Exception:
            if attempt == 2:
                return False, "other", None
            await asyncio.sleep(1)
            continue

    return False, "other", None


# ═══════════════════════════════════════════════
# CORE
# ═══════════════════════════════════════════════
async def _do_broadcast(
    message: Message,
    source_msg: Message,
    send_users: bool,
    send_groups: bool,
):
    user_ids = await clone_db.get_all_user_ids() if send_users else []
    group_ids = await clone_db.get_all_group_ids() if send_groups else []
    group_count_db = await get_all_registered_groups_count()

    total = len(user_ids) + len(group_ids)
    if total == 0:
        return await message.reply(
            "📢 ɴᴏ ᴜꜱᴇʀꜱ ᴏʀ ɢʀᴏᴜᴘꜱ ʀᴇɢɪꜱᴛᴇʀᴇᴅ ʏᴇᴛ."
        )

    status_msg = await message.reply(
        "📢 <b>ʙʀᴏᴀᴅᴄᴀꜱᴛ ꜱᴛᴀʀᴛᴇᴅ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 ᴜꜱᴇʀꜱ: <b>{len(user_ids)}</b>\n"
        f"👥 ɢʀᴏᴜᴘꜱ: <b>{len(group_ids)}</b>\n"
        f"📨 ᴛᴏᴛᴀʟ: <b>{total}</b>\n\n"
        "⏳ ꜱᴇɴᴅɪɴɢ..."
    )

    ok_users = blocked_users = deleted_users = other_users = 0
    ok_groups = blocked_groups = deleted_groups = other_groups = 0

    dead_user_ids: list[int] = []
    dead_group_ids: list[int] = []

    start = datetime.utcnow()

    # ═══ USERS ═══
    for i, uid in enumerate(user_ids, 1):
        ok, reason, to_delete = await _send_to(source_msg, uid)
        if ok:
            ok_users += 1
        elif reason == "blocked":
            blocked_users += 1
            if to_delete:
                dead_user_ids.append(to_delete)
        elif reason == "deleted":
            deleted_users += 1
            if to_delete:
                dead_user_ids.append(to_delete)
        else:
            other_users += 1
            print(f"❌ FAIL user {uid}: other")

        if i % 25 == 0:
            try:
                await status_msg.edit_text(
                    "📢 <b>ʙʀᴏᴀᴅᴄᴀꜱᴛ ɪɴ ᴘʀᴏɢʀᴇꜱꜱ</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"👥 ᴜꜱᴇʀꜱ: {i}/{len(user_ids)}\n"
                    f"✅ {ok_users} | 🚫 {blocked_users} | "
                    f"👻 {deleted_users} | ⚠️ {other_users}"
                )
            except Exception:
                pass

        await asyncio.sleep(DELAY_BETWEEN)

    # ═══ GROUPS ═══
    for i, gid in enumerate(group_ids, 1):
        ok, reason, to_delete = await _send_to(source_msg, gid)
        if ok:
            ok_groups += 1
        elif reason == "blocked":
            blocked_groups += 1
            if to_delete:
                dead_group_ids.append(to_delete)
        elif reason == "deleted":
            deleted_groups += 1
            if to_delete:
                dead_group_ids.append(to_delete)
        else:
            other_groups += 1
            print(f"❌ FAIL group {gid}: other")

        if i % 25 == 0:
            try:
                await status_msg.edit_text(
                    "📢 <b>ʙʀᴏᴀᴅᴄᴀꜱᴛ ɪɴ ᴘʀᴏɢʀᴇꜱꜱ</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"👥 ɢʀᴏᴜᴘꜱ: {i}/{len(group_ids)}\n"
                    f"✅ {ok_groups} | 🚫 {blocked_groups} | "
                    f"👻 {deleted_groups} | ⚠️ {other_groups}"
                )
            except Exception:
                pass

        await asyncio.sleep(DELAY_BETWEEN)

    elapsed = (datetime.utcnow() - start).total_seconds()

    # ═══ AUTO-CLEANUP dead users ═══
    removed_count = 0
    if dead_user_ids:
        try:
            removed_count = await get_dead_users_list(dead_user_ids)
            print(f"🧹 Auto-removed {removed_count} dead users from DB")
        except Exception as e:
            print(f"⚠️ Cleanup failed: {e}")

    stats = {
        "users_ok": ok_users,
        "users_blocked": blocked_users,
        "users_deleted": deleted_users,
        "users_other": other_users,
        "groups_ok": ok_groups,
        "groups_blocked": blocked_groups,
        "groups_deleted": deleted_groups,
        "groups_other": other_groups,
        "total_ok": ok_users + ok_groups,
        "total_fail": (
            blocked_users + deleted_users + other_users +
            blocked_groups + deleted_groups + other_groups
        ),
        "elapsed": elapsed,
        "timestamp": start.strftime("%Y-%m-%d %H:%M:%S"),
        "removed": removed_count,
        "groups_in_db": group_count_db,
    }
    _last_broadcast_stats[message.from_user.id] = stats

    report = (
        "✅ <b>ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴄᴏᴍᴘʟᴇᴛᴇ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "👥 <b>ᴜꜱᴇʀꜱ</b>\n"
        f"  ✅ ꜱᴜᴄᴄᴇꜱꜱ: <b>{ok_users}</b>\n"
        f"  🚫 ʙʟᴏᴄᴋᴇᴅ: <b>{blocked_users}</b>\n"
        f"  👻 ᴅᴇʟᴇᴛᴇᴅ: <b>{deleted_users}</b>\n"
        f"  ⚠️ ᴏᴛʜᴇʀ: <b>{other_users}</b>\n\n"
        "👥 <b>ɢʀᴏᴜᴘꜱ</b>\n"
        f"  ✅ ꜱᴜᴄᴄᴇꜱꜱ: <b>{ok_groups}</b>\n"
        f"  🚫 ʙʟᴏᴄᴋᴇᴅ: <b>{blocked_groups}</b>\n"
        f"  👻 ᴅᴇʟᴇᴛᴇᴅ: <b>{deleted_groups}</b>\n"
        f"  ⚠️ ᴏᴛʜᴇʀ: <b>{other_groups}</b>\n\n"
        "📊 <b>ᴛᴏᴛᴀʟ</b>\n"
        f"  ✅ ᴅᴇʟɪᴠᴇʀᴇᴅ: <b>{stats['total_ok']}</b>\n"
        f"  ❌ ꜰᴀɪʟᴇᴅ: <b>{stats['total_fail']}</b>\n\n"
        f"🧹 ᴅᴇᴀᴅ ᴜꜱᴇʀꜱ ʀᴇᴍᴏᴠᴇᴅ: <b>{removed_count}</b>\n"
        f"👥 ɢʀᴏᴜᴘꜱ ɪɴ ᴅʙ: <b>{group_count_db}</b>\n\n"
        f"⏱️ ᴛɪᴍᴇ: <b>{elapsed:.1f}s</b>"
    )

    try:
        await status_msg.edit_text(report)
    except Exception:
        await message.reply(report)


# ═══════════════════════════════════════════════
# /broadcast_stats
# ═══════════════════════════════════════════════
@router.message(Command("broadcast_stats"))
async def cmd_broadcast_stats(message: Message):
    if not _is_owner(message.from_user.id):
        return

    stats = _last_broadcast_stats.get(message.from_user.id)
    if not stats:
        return await message.reply("📊 ɴᴏ ʙʀᴏᴀᴅᴄᴀꜱᴛ ʀᴇᴄᴏʀᴅ ʏᴇᴛ.")

    await message.reply(
        "📊 <b>ʟᴀꜱᴛ ʙʀᴏᴀᴅᴄᴀꜱᴛ ꜱᴛᴀᴛꜱ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🕒 {stats['timestamp']}\n\n"
        f"👥 ᴜꜱᴇʀꜱ: ✅ {stats['users_ok']} | "
        f"🚫 {stats['users_blocked']} | "
        f"👻 {stats['users_deleted']} | "
        f"⚠️ {stats['users_other']}\n"
        f"👥 ɢʀᴏᴜᴘꜱ: ✅ {stats['groups_ok']} | "
        f"🚫 {stats['groups_blocked']} | "
        f"👻 {stats['groups_deleted']} | "
        f"⚠️ {stats['groups_other']}\n\n"
        f"📊 ᴛᴏᴛᴀʟ: ✅ {stats['total_ok']} | ❌ {stats['total_fail']}\n"
        f"🧹 ʀᴇᴍᴏᴠᴇᴅ: {stats.get('removed', 0)}\n"
        f"⏱️ ᴛɪᴍᴇ: {stats['elapsed']:.1f}s"
    )
