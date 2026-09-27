import logging
from aiogram import Router, F, Bot
from aiogram.filters import Command, ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER
from aiogram.types import (
    Message, CallbackQuery, ChatMemberUpdated, ChatPermissions,
)
from aiogram.exceptions import TelegramBadRequest

from keyboards.group_kb import group_settings_kb, locks_menu_kb
from utils.database import (
    get_or_create_group, toggle_group_setting, get_group_setting,
    set_lock, get_lock, get_all_locks, LOCK_TYPES,
    add_warning, get_warnings, remove_last_warning,
)
from utils.permissions import (
    is_bot_admin, has_right, is_group_admin, get_group_member,
)
from utils.ui import smart_edit

router = Router()
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════
# WELCOME / GOODBYE
# ═══════════════════════════════════════════════
@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def welcome_member(event: ChatMemberUpdated):
    try:
        if not await get_group_setting(event.chat.id, "welcome_enabled"):
            return
    except Exception:
        pass

    user = event.new_chat_member.user
    bot = event.bot

    # PFP
    pfp = None
    try:
        photos = await bot.get_user_profile_photos(user.id, limit=1)
        if photos.total_count:
            pfp = photos.photos[0][-1].file_id
    except Exception:
        pass

    # Bio
    bio = "вiσ ησт sєᴛ"
    try:
        chat_info = await bot.get_chat(user.id)
        if chat_info.bio:
            bio = chat_info.bio
    except Exception:
        pass

    username = f"@{user.username}" if user.username else "ᴜsєʀηᴧᴍє ησт sєᴛ"
    mention = user.mention_html()

    # Live member count
    try:
        members = await bot.get_chat_member_count(event.chat.id)
    except Exception:
        members = "?"

    text = (
        f"🌌 <b>ᴧ ηєᴡ sᴛᴧʀ єηᴛєʀєᴅ</b> 🌌\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"✦ ηᴧᴍє → {mention}\n"
        f"✦ ᴜsєʀηᴧᴍє → {username}\n"
        f"✦ ɪᴅ → <code>{user.id}</code>\n"
        f"✦ ʙɪᴏ → {bio}\n"
        f"✦ ᴍєᴍʙєʀs → {members}\n\n"
        f"🌸 sᴛᴧʏ нᴧᴩᴩʏ! 🌸"
    )

    try:
        if pfp:
            await bot.send_photo(event.chat.id, photo=pfp, caption=text)
        else:
            await bot.send_message(event.chat.id, text)
    except Exception as e:
        logger.warning(f"Welcome failed: {e}")


@router.chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))
async def goodbye_member(event: ChatMemberUpdated):
    try:
        if not await get_group_setting(event.chat.id, "goodbye_enabled"):
            return
    except Exception:
        pass
    user = event.new_chat_member.user
    text = (
        f"👋 <b>ɢᴏᴏᴅʙʏє!</b>\n\n"
        f"{user.mention_html()} ʜᴀs ʟᴇғᴛ ᴛʜᴇ ɢʀᴏᴜᴘ.\n"
        f"🌸 ᴡᴇ'ʟʟ ᴍɪss ʏᴏᴜ!"
    )
    try:
        await event.bot.send_message(event.chat.id, text)
    except Exception:
        pass


# ═══════════════════════════════════════════════
# GROUP SETTINGS
# ═══════════════════════════════════════════════
@router.message(Command("settings"))
async def cmd_settings(message: Message, bot: Bot):
    if message.chat.type == "private":
        await message.reply("ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs ᴏɴʟʏ.")
        return
    if not await has_right(bot, message.chat.id, message.from_user.id, "can_change_info"):
        await message.reply("❌ ʏᴏᴜ ɴᴇᴇᴅ ᴄʜᴀɴɢᴇ-ɪɴғᴏ ᴀᴅᴍɪɴ ʀɪɢʜᴛ.")
        return

    await get_or_create_group(message.chat.id)
    settings = {}
    for key in ("welcome_enabled", "goodbye_enabled", "antilink", "antiflood", "antiforward", "captcha"):
        settings[key] = await get_group_setting(message.chat.id, key)

    text = (
        f"⚙️ <b>ɢʀᴏᴜᴘ sᴇᴛᴛɪɴɢs</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ᴛᴀᴘ ᴛᴏ ᴛᴏɢɢʟᴇ:"
    )
    await message.answer(text, reply_markup=group_settings_kb(message.chat.id, settings))


@router.callback_query(F.data == "grp:settings")
async def cb_settings(cb: CallbackQuery, bot: Bot):
    if not await has_right(bot, cb.message.chat.id, cb.from_user.id, "can_change_info"):
        await cb.answer("❌ ɴᴏ ᴘᴇʀᴍɪssɪᴏɴ", show_alert=True)
        return
    settings = {}
    for key in ("welcome_enabled", "goodbye_enabled", "antilink", "antiflood", "antiforward", "captcha"):
        settings[key] = await get_group_setting(cb.message.chat.id, key)
    text = f"⚙️ <b>ɢʀᴏᴜᴘ sᴇᴛᴛɪɴɢs</b>\n━━━━━━━━━━━━━━━━━━━━━\n\nᴛᴀᴘ ᴛᴏ ᴛᴏɢɢʟᴇ:"
    await smart_edit(cb, text, group_settings_kb(cb.message.chat.id, settings))
    await cb.answer()


@router.callback_query(F.data.startswith("grp:toggle:"))
async def cb_toggle(cb: CallbackQuery, bot: Bot):
    if not await has_right(bot, cb.message.chat.id, cb.from_user.id, "can_change_info"):
        await cb.answer("❌ ɴᴏ ᴘᴇʀᴍɪssɪᴏɴ", show_alert=True)
        return
    setting = cb.data.split(":")[2]
    new_val = await toggle_group_setting(cb.message.chat.id, setting)
    await cb.answer(f"{'✅ ᴏɴ' if new_val else '❌ ᴏғғ'}")

    settings = {}
    for key in ("welcome_enabled", "goodbye_enabled", "antilink", "antiflood", "antiforward", "captcha"):
        settings[key] = await get_group_setting(cb.message.chat.id, key)
    text = f"⚙️ <b>ɢʀᴏᴜᴘ sᴇᴛᴛɪɴɢs</b>\n━━━━━━━━━━━━━━━━━━━━━\n\nᴛᴀᴘ ᴛᴏ ᴛᴏɢɢʟᴇ:"
    await smart_edit(cb, text, group_settings_kb(cb.message.chat.id, settings))


# ═══════════════════════════════════════════════
# LOCKS
# ═══════════════════════════════════════════════
@router.callback_query(F.data == "grp:locks")
async def cb_locks(cb: CallbackQuery, bot: Bot):
    if not await has_right(bot, cb.message.chat.id, cb.from_user.id, "can_change_info"):
        await cb.answer("❌ ɴᴏ ᴘᴇʀᴍɪssɪᴏɴ", show_alert=True)
        return
    locks = await get_all_locks(cb.message.chat.id)
    text = (
        f"🔒 <b>ɢʀᴏᴜᴘ ʟᴏᴄᴋs</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔒 = ʟᴏᴄᴋᴇᴅ | 🔓 = ᴜɴʟᴏᴄᴋᴇᴅ\n\n"
        f"ᴛᴀᴘ ᴛᴏ ᴛᴏɢɢʟᴇ:"
    )
    await smart_edit(cb, text, locks_menu_kb(locks))
    await cb.answer()


@router.callback_query(F.data.startswith("grp:lock:"))
async def cb_lock_toggle(cb: CallbackQuery, bot: Bot):
    if not await has_right(bot, cb.message.chat.id, cb.from_user.id, "can_change_info"):
        await cb.answer("❌ ɴᴏ ᴘᴇʀᴍɪssɪᴏɴ", show_alert=True)
        return
    lock_type = cb.data.split(":")[2]
    current = await get_lock(cb.message.chat.id, lock_type)
    new_val = 0 if current else 1
    await set_lock(cb.message.chat.id, lock_type, new_val)
    await cb.answer(f"{'🔒 ʟᴏᴄᴋᴇᴅ' if new_val else '🔓 ᴜɴʟᴏᴄᴋᴇᴅ'} {lock_type}")

    locks = await get_all_locks(cb.message.chat.id)
    text = (
        f"🔒 <b>ɢʀᴏᴜᴘ ʟᴏᴄᴋs</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔒 = ʟᴏᴄᴋᴇᴅ | 🔓 = ᴜɴʟᴏᴄᴋᴇᴅ\n\n"
        f"ᴛᴀᴘ ᴛᴏ ᴛᴏɢɢʟᴇ:"
    )
    await smart_edit(cb, text, locks_menu_kb(locks))


# Text commands for locks
@router.message(Command("lock"))
async def cmd_lock(message: Message, bot: Bot):
    if not await has_right(bot, message.chat.id, message.from_user.id, "can_change_info"):
        return await message.reply("❌ ɴᴏ ᴘᴇʀᴍɪssɪᴏɴ.")
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("ᴜsᴀɢᴇ: /lock <type>\nᴛʏᴘᴇs: " + ", ".join(LOCK_TYPES))
    lt = args[1].lower().strip()
    if lt not in LOCK_TYPES:
        return await message.reply(f"❌ ɪɴᴠᴀʟɪᴅ. ᴛʏᴘᴇs: {', '.join(LOCK_TYPES)}")
    await set_lock(message.chat.id, lt, 1)
    await message.reply(f"🔒 {lt} ʟᴏᴄᴋᴇᴅ.")


@router.message(Command("unlock"))
async def cmd_unlock(message: Message, bot: Bot):
    if not await has_right(bot, message.chat.id, message.from_user.id, "can_change_info"):
        return await message.reply("❌ ɴᴏ ᴘᴇʀᴍɪssɪᴏɴ.")
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("ᴜsᴀɢᴇ: /unlock <type>")
    lt = args[1].lower().strip()
    if lt not in LOCK_TYPES:
        return await message.reply(f"❌ ɪɴᴠᴀʟɪᴅ. ᴛʏᴘᴇs: {', '.join(LOCK_TYPES)}")
    await set_lock(message.chat.id, lt, 0)
    await message.reply(f"🔓 {lt} ᴜɴʟᴏᴄᴋᴇᴅ.")


# ═══════════════════════════════════════════════
# MODERATION
# ═══════════════════════════════════════════════
@router.message(Command("warn"))
async def cmd_warn(message: Message, bot: Bot):
    if not await has_right(bot, message.chat.id, message.from_user.id, "can_restrict_members"):
        return await message.reply("❌ ɴᴏ ᴘᴇʀᴍɪssɪᴏɴ.")
    if not message.reply_to_message:
        return await message.reply("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ.")
    target = message.reply_to_message.from_user
    if await is_group_admin(bot, message.chat.id, target.id):
        return await message.reply("❌ ᴄᴀɴ'ᴛ ᴡᴀʀɴ ᴀɴ ᴀᴅᴍɪɴ.")
    reason = message.text.replace("/warn", "", 1).strip() or "No reason"
    await add_warning(target.id, message.chat.id, reason, message.from_user.id)
    count = await get_warnings(target.id, message.chat.id)
    await message.reply(
        f"⚠️ {target.mention_html()} ᴡᴀʀɴᴇᴅ.\nʀᴇᴀsᴏɴ: {reason}\nᴛᴏᴛᴀʟ: <b>{count}/3</b>"
    )
    if count >= 3:
        try:
            await bot.restrict_chat_member(
                message.chat.id, target.id,
                permissions=ChatPermissions(can_send_messages=False)
            )
            await message.answer(f"🔇 {target.mention_html()} ᴀᴜᴛᴏ-ᴍᴜᴛᴇᴅ (3 ᴡᴀʀɴs).")
        except Exception as e:
            logger.warning(f"Auto-mute failed: {e}")


@router.message(Command("warnings"))
async def cmd_warnings(message: Message):
    if not message.reply_to_message:
        return await message.reply("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ.")
    target = message.reply_to_message.from_user
    count = await get_warnings(target.id, message.chat.id)
    await message.reply(f"⚠️ {target.mention_html()} ʜᴀs <b>{count}</b> ᴡᴀʀɴɪɴɢs.")


@router.message(Command("unwarn"))
async def cmd_unwarn(message: Message, bot: Bot):
    if not await has_right(bot, message.chat.id, message.from_user.id, "can_restrict_members"):
        return await message.reply("❌ ɴᴏ ᴘᴇʀᴍɪssɪᴏɴ.")
    if not message.reply_to_message:
        return await message.reply("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ.")
    target = message.reply_to_message.from_user
    ok = await remove_last_warning(target.id, message.chat.id)
    if ok:
        count = await get_warnings(target.id, message.chat.id)
        await message.reply(f"✅ ʀᴇᴍᴏᴠᴇᴅ ᴏɴᴇ ᴡᴀʀɴɪɴɢ. ɴᴏᴡ: <b>{count}</b>")
    else:
        await message.reply("ηᴏ ᴡᴀʀɴɪɴɢs ᴛᴏ ʀᴇᴍᴏᴠᴇ.")


@router.message(Command("mute"))
async def cmd_mute(message: Message, bot: Bot):
    if not await has_right(bot, message.chat.id, message.from_user.id, "can_restrict_members"):
        return await message.reply("❌ ɴᴏ ᴘᴇʀᴍɪssɪᴏɴ.")
    if not message.reply_to_message:
        return await message.reply("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ.")
    target = message.reply_to_message.from_user
    if await is_group_admin(bot, message.chat.id, target.id):
        return await message.reply("❌ ᴄᴀɴ'ᴛ ᴍᴜᴛᴇ ᴀɴ ᴀᴅᴍɪɴ.")
    try:
        await bot.restrict_chat_member(
            message.chat.id, target.id,
            permissions=ChatPermissions(can_send_messages=False)
        )
        await message.reply(f"🔇 {target.mention_html()} ᴍᴜᴛᴇᴅ.")
    except Exception as e:
        await message.reply(f"❌ ғᴀɪʟᴇᴅ: {e}")


@router.message(Command("unmute"))
async def cmd_unmute(message: Message, bot: Bot):
    if not await has_right(bot, message.chat.id, message.from_user.id, "can_restrict_members"):
        return await message.reply("❌ ɴᴏ ᴘᴇʀᴍɪssɪᴏɴ.")
    if not message.reply_to_message:
        return await message.reply("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ.")
    target = message.reply_to_message.from_user
    try:
        await bot.restrict_chat_member(
            message.chat.id, target.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            )
        )
        await message.reply(f"🔊 {target.mention_html()} ᴜɴᴍᴜᴛᴇᴅ.")
    except Exception as e:
        await message.reply(f"❌ ғᴀɪʟᴇᴅ: {e}")


@router.message(Command("kick"))
async def cmd_kick(message: Message, bot: Bot):
    if not await has_right(bot, message.chat.id, message.from_user.id, "can_restrict_members"):
        return await message.reply("❌ ɴᴏ ᴘᴇʀᴍɪssɪᴏɴ.")
    if not message.reply_to_message:
        return await message.reply("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ.")
    target = message.reply_to_message.from_user
    if await is_group_admin(bot, message.chat.id, target.id):
        return await message.reply("❌ ᴄᴀɴ'ᴛ ᴋɪᴄᴋ ᴀɴ ᴀᴅᴍɪɴ.")
    try:
        await bot.ban_chat_member(message.chat.id, target.id)
        await bot.unban_chat_member(message.chat.id, target.id)
        await message.reply(f"👢 {target.mention_html()} ᴋɪᴄᴋᴇᴅ.")
    except Exception as e:
        await message.reply(f"❌ ғᴀɪʟᴇᴅ: {e}")


@router.message(Command("ban"))
async def cmd_ban(message: Message, bot: Bot):
    if not await has_right(bot, message.chat.id, message.from_user.id, "can_restrict_members"):
        return await message.reply("❌ ɴᴏ ᴘᴇʀᴍɪssɪᴏɴ.")
    if not message.reply_to_message:
        return await message.reply("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ.")
    target = message.reply_to_message.from_user
    if await is_group_admin(bot, message.chat.id, target.id):
        return await message.reply("❌ ᴄᴀɴ'ᴛ ʙᴀɴ ᴀɴ ᴀᴅᴍɪɴ.")
    try:
        await bot.ban_chat_member(message.chat.id, target.id)
        await message.reply(f"🚫 {target.mention_html()} ʙᴀɴɴᴇᴅ.")
    except Exception as e:
        await message.reply(f"❌ ғᴀɪʟᴇᴅ: {e}")


@router.message(Command("unban"))
async def cmd_unban(message: Message, bot: Bot):
    if not await has_right(bot, message.chat.id, message.from_user.id, "can_restrict_members"):
        return await message.reply("❌ ɴᴏ ᴘᴇʀᴍɪssɪᴏɴ.")
    if not message.reply_to_message:
        return await message.reply("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ.")
    target = message.reply_to_message.from_user
    try:
        await bot.unban_chat_member(message.chat.id, target.id)
        await message.reply(f"✅ {target.mention_html()} ᴜɴʙᴀɴɴᴇᴅ.")
    except Exception as e:
        await message.reply(f"❌ ғᴀɪʟᴇᴅ: {e}")


@router.message(Command("purge"))
async def cmd_purge(message: Message, bot: Bot):
    if not await has_right(bot, message.chat.id, message.from_user.id, "can_delete_messages"):
        return await message.reply("❌ ɴᴏ ᴘᴇʀᴍɪssɪᴏɴ.")
    if not message.reply_to_message:
        return await message.reply("ʀᴇᴘʟʏ ᴛᴏ ᴛʜᴇ sᴛᴀʀᴛ ᴍᴇssᴀɢᴇ ᴛᴏ ᴘᴜʀɢᴇ ᴜᴘ ᴛᴏ ʜᴇʀᴇ.")
    try:
        await bot.delete_message(message.chat.id, message.message_id)
        start_id = message.reply_to_message.message_id
        end_id = message.message_id
        deleted = 0
        for mid in range(start_id, end_id + 1):
            try:
                await bot.delete_message(message.chat.id, mid)
                deleted += 1
            except Exception:
                pass
        confirm = await message.answer(f"🧹 ᴅᴇʟᴇᴛᴇᴅ {deleted} ᴍᴇssᴀɢᴇ(s).")
        import asyncio
        await asyncio.sleep(3)
        await confirm.delete()
    except Exception as e:
        await message.reply(f"❌ ғᴀɪʟᴇᴅ: {e}")


# ═══════════════════════════════════════════════
# AUTO-MOD: Locks + Antilink + Antiflood
# ═══════════════════════════════════════════════
import re
import time
from collections import defaultdict

_flood_tracker = defaultdict(list)
URL_PATTERN = re.compile(r"(https?://|t\.me/|telegram\.me/|www\.)", re.IGNORECASE)


@router.message(F.chat.type.in_({"group", "supergroup"}))
async def auto_mod(message: Message, bot: Bot):
    if not message.from_user:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id

    # Skip admins
    try:
        member = await get_group_member(bot, chat_id, user_id)
        from aiogram.types import ChatMemberOwner, ChatMemberAdministrator
        if isinstance(member, (ChatMemberOwner, ChatMemberAdministrator)):
            return
    except Exception:
        pass

    # ═══ Antilink ═══
    if await get_group_setting(chat_id, "antilink"):
        if message.text and URL_PATTERN.search(message.text):
            try:
                await message.delete()
                await message.answer(f"🔗 {message.from_user.mention_html()}, ʟɪɴᴋs ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ.")
            except Exception:
                pass
            return

    # ═══ Antiforward ═══
    if await get_group_setting(chat_id, "antiforward"):
        if message.forward_date or message.forward_from or message.forward_from_chat:
            try:
                await message.delete()
                await message.answer(f"↪️ {message.from_user.mention_html()}, ғᴏʀᴡᴀʀᴅs ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ.")
            except Exception:
                pass
            return

    # ═══ Locks ═══
    checks = [
        ("stickers", message.sticker is not None),
        ("gifs", message.animation is not None),
        ("photos", message.photo is not None),
        ("videos", message.video is not None),
        ("documents", message.document is not None),
        ("audio", message.audio is not None),
        ("voice", message.voice is not None),
        ("polls", message.poll is not None),
        ("contacts", message.contact is not None),
        ("forwards", bool(message.forward_date)),
        ("links", bool(message.text and URL_PATTERN.search(message.text))),
    ]
    for lock_type, is_present in checks:
        if is_present and await get_lock(chat_id, lock_type):
            try:
                await message.delete()
            except Exception:
                pass
            try:
                await message.answer(
                    f"🔒 {message.from_user.mention_html()}, {lock_type} ɪs ʟᴏᴄᴋᴇᴅ.",
                    disable_notification=True,
                )
            except Exception:
                pass
            return

    # ═══ Antiflood ═══
    if await get_group_setting(chat_id, "antiflood"):
        now = time.time()
        _flood_tracker[user_id] = [t for t in _flood_tracker[user_id] if now - t < 10]
        _flood_tracker[user_id].append(now)
        if len(_flood_tracker[user_id]) > 10:
            try:
                await bot.restrict_chat_member(
                    chat_id, user_id,
                    permissions=ChatPermissions(can_send_messages=False),
                    until_date=int(now) + 300,
                )
                await message.answer(f"🌊 {message.from_user.mention_html()} ᴍᴜᴛᴇᴅ 5ᴍ ʙʏ ᴀɴᴛɪғʟᴏᴏᴅ.")
            except Exception:
                pass
