"""
handlers/broadcast.py — Owner-only broadcast system.

Commands (OWNER_IDS only):
  /broadcast         — reply to any message → send to all users + groups
  /broadcast_users   — users only
  /broadcast_groups  — groups only
  /broadcast_stats   — view last broadcast stats

Scope:
  Main bot only. Does NOT iterate over clones.
"""

import asyncio
from datetime import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from config import OWNER_IDS
from utils import clone_db

router = Router()


# In-memory last broadcast stats (per owner)
_last_broadcast_stats: dict = {}


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

    ok_users = fail_users = 0
    ok_groups = fail_groups = 0
    start = datetime.utcnow()

    # ── Users ──
    for i, uid in enumerate(user_ids, 1):
        try:
            await source_msg.copy_to(chat_id=uid)
            ok_users += 1
        except (TelegramForbiddenError, TelegramBadRequest):
            fail_users += 1
        except Exception:
            fail_users += 1

        if i % 25 == 0:
            try:
                await status_msg.edit_text(
                    "📢 <b>ʙʀᴏᴀᴅᴄᴀꜱᴛ ɪɴ ᴘʀᴏɢʀᴇꜱꜱ</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"👥 ᴜꜱᴇʀꜱ: {i}/{len(user_ids)}\n"
                    f"📊 ✅ {ok_users} | ❌ {fail_users}"
                )
            except Exception:
                pass

        await asyncio.sleep(0.05)

    # ── Groups ──
    for i, gid in enumerate(group_ids, 1):
        try:
            await source_msg.copy_to(chat_id=gid)
            ok_groups += 1
        except (TelegramForbiddenError, TelegramBadRequest):
            fail_groups += 1
        except Exception:
            fail_groups += 1

        if i % 25 == 0:
            try:
                await status_msg.edit_text(
                    "📢 <b>ʙʀᴏᴀᴅᴄᴀꜱᴛ ɪɴ ᴘʀᴏɢʀᴇꜱꜱ</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"👥 ɢʀᴏᴜᴘꜱ: {i}/{len(group_ids)}\n"
                    f"📊 ✅ {ok_groups} | ❌ {fail_groups}"
                )
            except Exception:
                pass

        await asyncio.sleep(0.05)

    elapsed = (datetime.utcnow() - start).total_seconds()

    stats = {
        "users_ok": ok_users, "users_fail": fail_users,
        "groups_ok": ok_groups, "groups_fail": fail_groups,
        "total_ok": ok_users + ok_groups,
        "total_fail": fail_users + fail_groups,
        "elapsed": elapsed,
        "timestamp": start.strftime("%Y-%m-%d %H:%M:%S"),
    }
    _last_broadcast_stats[message.from_user.id] = stats

    report = (
        "✅ <b>ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴄᴏᴍᴘʟᴇᴛᴇ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "👥 <b>ᴜꜱᴇʀꜱ</b>\n"
        f"  ✅ ꜱᴜᴄᴄᴇꜱꜱ: <b>{ok_users}</b>\n"
        f"  ❌ ꜰᴀɪʟᴇᴅ: <b>{fail_users}</b>\n\n"
        "👥 <b>ɢʀᴏᴜᴘꜱ</b>\n"
        f"  ✅ ꜱᴜᴄᴄᴇꜱꜱ: <b>{ok_groups}</b>\n"
        f"  ❌ ꜰᴀɪʟᴇᴅ: <b>{fail_groups}</b>\n\n"
        "📊 <b>ᴛᴏᴛᴀʟ</b>\n"
        f"  ✅ ᴅᴇʟɪᴠᴇʀᴇᴅ: <b>{stats['total_ok']}</b>\n"
        f"  ❌ ꜰᴀɪʟᴇᴅ: <b>{stats['total_fail']}</b>\n\n"
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
        f"👥 ᴜꜱᴇʀꜱ: ✅ {stats['users_ok']} | ❌ {stats['users_fail']}\n"
        f"👥 ɢʀᴏᴜᴘꜱ: ✅ {stats['groups_ok']} | ❌ {stats['groups_fail']}\n\n"
        f"📊 ᴛᴏᴛᴀʟ: ✅ {stats['total_ok']} | ❌ {stats['total_fail']}\n"
        f"⏱️ ᴛɪᴍᴇ: {stats['elapsed']:.1f}s"
    )
