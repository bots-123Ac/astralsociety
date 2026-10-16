"""
handlers/required_chat.py — Owner-only commands to manage required chats.

Commands (OWNER_IDS only):
  /addrequired              — reply in a channel/GC, or pass chat id/username
  /removerequired -100xxx   — remove a required chat
  /listrequired             — show all required chats

Note:
  The MAIN bot must be an admin in the required channel/group so it can
  verify membership via get_chat_member().
"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import OWNER_IDS
from utils import clone_db

router = Router()


def _is_owner(user_id: int) -> bool:
    return user_id in OWNER_IDS


# ═══════════════════════════════════════════════
# /addrequired
# ═══════════════════════════════════════════════
@router.message(Command("addrequired"))
async def cmd_addrequired(message: Message):
    if not _is_owner(message.from_user.id):
        return  # silent ignore

    target_chat_id = None
    target_username = None

    args = (message.text or "").split(maxsplit=1)
    if len(args) > 1:
        arg = args[1].strip()
        if arg.lstrip("-").isdigit():
            try:
                target_chat_id = int(arg)
            except ValueError:
                return await message.reply("❌ ɪɴᴠᴀʟɪᴅ ᴄʜᴀᴛ ɪᴅ.")
        elif arg.startswith("@"):
            target_username = arg
        else:
            return await message.reply(
                "❌ <b>ᴜꜱᴀɢᴇ:</b>\n"
                "<code>/addrequired -100xxxxxxxxx</code>\n"
                "<code>/addrequired @channelusername</code>\n"
                "ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇꜱꜱᴀɢᴇ ɪɴ ᴛʜᴇ ᴄʜᴀᴛ."
            )
    elif message.reply_to_message:
        target_chat_id = message.chat.id
    else:
        return await message.reply(
            "❌ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴄʜᴀᴛ ɪᴅ/ᴜꜱᴇʀɴᴀᴍᴇ, ᴏʀ ʀᴇᴘʟʏ ɪɴ ᴛʜᴇ ᴄʜᴀᴛ."
        )

    # Fetch chat info
    try:
        if target_chat_id is not None:
            chat = await message.bot.get_chat(target_chat_id)
        else:
            chat = await message.bot.get_chat(target_username)
    except Exception as e:
        return await message.reply(
            "❌ <b>ᴄᴀɴ'ᴛ ꜰᴇᴛᴄʜ ᴄʜᴀᴛ ɪɴꜰᴏ.</b>\n\n"
            "ᴍᴀᴋᴇ ꜱᴜʀᴇ ᴛʜᴇ ʙᴏᴛ ɪꜱ ᴀ ᴍᴇᴍʙᴇʀ (ᴘʀᴇꜰᴇʀᴀʙʟʏ ᴀᴅᴍɪɴ).\n"
            f"<code>{str(e)[:150]}</code>"
        )

    # Build invite link
    invite_link = None
    if chat.username:
        invite_link = f"https://t.me/{chat.username}"
    else:
        try:
            link_obj = await message.bot.create_chat_invite_link(chat.id)
            invite_link = link_obj.invite_link
        except Exception:
            pass

    await clone_db.add_required_chat(
        chat_id=chat.id,
        chat_username=chat.username,
        chat_title=chat.title or chat.full_name or str(chat.id),
        chat_type=chat.type,
        invite_link=invite_link,
    )

    await message.reply(
        "✅ <b>ᴀᴅᴅᴇᴅ ᴛᴏ ʀᴇQᴜɪʀᴇᴅ ʟɪꜱᴛ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📛 {chat.title or chat.full_name}\n"
        f"🆔 <code>{chat.id}</code>\n"
        f"🔗 {invite_link or '—'}"
    )


# ═══════════════════════════════════════════════
# /removerequired
# ═══════════════════════════════════════════════
@router.message(Command("removerequired"))
async def cmd_removerequired(message: Message):
    if not _is_owner(message.from_user.id):
        return

    args = (message.text or "").split(maxsplit=1)
    if len(args) < 2:
        return await message.reply(
            "ᴜꜱᴀɢᴇ: <code>/removerequired -100xxxxxxxxx</code>"
        )

    try:
        chat_id = int(args[1].strip())
    except ValueError:
        return await message.reply("❌ ɪɴᴠᴀʟɪᴅ ᴄʜᴀᴛ ɪᴅ.")

    ok = await clone_db.remove_required_chat(chat_id)
    if ok:
        await message.reply(f"✅ ʀᴇᴍᴏᴠᴇᴅ <code>{chat_id}</code>.")
    else:
        await message.reply(f"❌ ᴄʜᴀᴛ <code>{chat_id}</code> ɴᴏᴛ ꜰᴏᴜɴᴅ.")


# ═══════════════════════════════════════════════
# /listrequired
# ═══════════════════════════════════════════════
@router.message(Command("listrequired"))
async def cmd_listrequired(message: Message):
    if not _is_owner(message.from_user.id):
        return

    chats = await clone_db.get_all_required_chats()
    if not chats:
        return await message.reply(
            "📋 <b>ʀᴇQᴜɪʀᴇᴅ ᴄʜᴀᴛꜱ</b>\n\n"
            "❌ ɴᴏɴᴇ ꜱᴇᴛ ʏᴇᴛ.\n"
            "ᴜꜱᴇ /addrequired ᴛᴏ ᴀᴅᴅ."
        )

    lines = [
        f"📋 <b>ʀᴇQᴜɪʀᴇᴅ ᴄʜᴀᴛꜱ ({len(chats)})</b>",
        "━━━━━━━━━━━━━━━━━━━━━",
        "",
    ]
    for i, chat in enumerate(chats, 1):
        lines.append(
            f"{i}. <b>{chat['chat_title']}</b>\n"
            f"   🆔 <code>{chat['chat_id']}</code>\n"
            f"   📝 {chat['chat_type']}\n"
            f"   🔗 {chat['invite_link'] or '—'}"
        )
    await message.reply(
        "\n".join(lines), disable_web_page_preview=True
    )
