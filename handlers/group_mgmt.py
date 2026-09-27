from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    ChatMemberUpdated, Message, CallbackQuery,
)
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER

from config import BOT_NAME
from utils.database import (
    get_or_create_group, toggle_group_setting, get_group_setting,
    add_warning, get_warnings,
)
from utils.permissions import is_admin

router = Router()


# ─── WELCOME / GOODBYE ───
@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def welcome(event: ChatMemberUpdated):
    try:
        enabled = await get_group_setting(event.chat.id, "welcome_enabled")
        if not enabled:
            return
    except Exception:
        pass

    user = event.new_chat_member.user
    try:
        photos = await event.bot.get_user_profile_photos(user.id, limit=1)
        pfp = photos.photos[0][-1].file_id if photos.total_count else None
    except Exception:
        pfp = None

    try:
        chat_info = await event.bot.get_chat(user.id)
        bio = chat_info.bio or "вiσ ησт sєᴛ"
    except Exception:
        bio = "вiσ ησт sєᴛ"

    username = f"@{user.username}" if user.username else "ᴜsєʀηᴧᴍє ησт sєᴛ"
    mention = user.mention_html()
    try:
        members = await event.bot.get_chat_members_count(event.chat.id)
    except Exception:
        members = "?"

    text = (
        f"🌌 <b>ᴧ ηєᴡ sᴛᴧʀ ᴇηᴛᴇʀᴇᴅ</b> 🌌\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"✦ ηᴧᴍє → {mention}\n"
        f"✦ ᴜsᴇʀηᴧᴍє → {username}\n"
        f"✦ ɪᴅ → <code>{user.id}</code>\n"
        f"✦ ʙɪᴏ → {bio}\n"
        f"✦ ᴍᴇᴍʙᴇʀs → {members}\n\n"
        f"🌸 sᴛᴀʏ ʜᴀᴘᴘʏ! 🌸\n"
        f"🚀 ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ {BOT_NAME}"
    )
    try:
        if pfp:
            await event.bot.send_photo(event.chat.id, photo=pfp, caption=text)
        else:
            await event.bot.send_message(event.chat.id, text)
    except Exception:
        pass


@router.chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))
async def goodbye(event: ChatMemberUpdated):
    try:
        enabled = await get_group_setting(event.chat.id, "goodbye_enabled")
        if not enabled:
            return
    except Exception:
        pass
    user = event.new_chat_member.user
    text = (
        f"👋 <b>ɢᴏᴏᴅʙʏᴇ!</b>\n\n"
        f"{user.mention_html()} ʜᴀs ʟᴇғᴛ ᴛʜᴇ ɢʀᴏᴜᴘ.\n"
        f"🌸 ᴡᴇ'ʟʟ ᴍɪss ʏᴏᴜ!"
    )
    try:
        await event.bot.send_message(event.chat.id, text)
    except Exception:
        pass


# ─── WARN ───
@router.message(Command("warn"))
async def cmd_warn(message: Message):
    if not is_admin(message.from_user.id):
        await message.reply("❌ ᴀᴅᴍɪɴs ᴏɴʟʏ.")
        return
    if not message.reply_to_message:
        await message.reply("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ ᴛᴏ ᴡᴀʀɴ.")
        return
    target = message.reply_to_message.from_user
    reason = message.text.replace("/warn", "").strip() or "No reason"
    await add_warning(target.id, message.chat.id, reason, message.from_user.id)
    count = await get_warnings(target.id, message.chat.id)
    await message.reply(
        f"⚠️ {target.mention_html()} ᴡᴀʀɴᴇᴅ.\n"
        f"ʀᴇᴀsᴏɴ: {reason}\n"
        f"ᴛᴏᴛᴀʟ ᴡᴀʀɴɪɴɢs: <b>{count}</b>"
    )


@router.message(Command("warnings"))
async def cmd_warnings(message: Message):
    if not message.reply_to_message:
        await message.reply("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ.")
        return
    target = message.reply_to_message.from_user
    count = await get_warnings(target.id, message.chat.id)
    await message.reply(f"⚠️ {target.mention_html()} ʜᴀs <b>{count}</b> ᴡᴀʀɴɪɴɢs.")


# ─── MUTE / KICK / BAN ───
@router.message(Command("mute"))
async def cmd_mute(message: Message):
    if not is_admin(message.from_user.id):
        return
    if not message.reply_to_message:
        return await message.reply("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ.")
    target = message.reply_to_message.from_user
    try:
        from aiogram.types import ChatPermissions
        await message.chat.restrict(
            user_id=target.id,
            permissions=ChatPermissions(can_send_messages=False),
        )
        await message.reply(f"🔇 {target.mention_html()} ᴍᴜᴛᴇᴅ.")
    except Exception as e:
        await message.reply(f"❌ ғᴀɪʟᴇᴅ: {e}")


@router.message(Command("unmute"))
async def cmd_unmute(message: Message):
    if not is_admin(message.from_user.id):
        return
    if not message.reply_to_message:
        return await message.reply("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ.")
    target = message.reply_to_message.from_user
    try:
        from aiogram.types import ChatPermissions
        await message.chat.restrict(
            user_id=target.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            ),
        )
        await message.reply(f"🔊 {target.mention_html()} ᴜɴᴍᴜᴛᴇᴅ.")
    except Exception as e:
        await message.reply(f"❌ ғᴀɪʟᴇᴅ: {e}")


@router.message(Command("kick"))
async def cmd_kick(message: Message):
    if not is_admin(message.from_user.id):
        return
    if not message.reply_to_message:
        return await message.reply("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ.")
    target = message.reply_to_message.from_user
    try:
        await message.chat.ban(user_id=target.id)
        await message.chat.unban(user_id=target.id)
        await message.reply(f"👢 {target.mention_html()} ᴋɪᴄᴋᴇᴅ.")
    except Exception as e:
        await message.reply(f"❌ ғᴀɪʟᴇᴅ: {e}")


@router.message(Command("ban"))
async def cmd_ban(message: Message):
    if not is_admin(message.from_user.id):
        return
    if not message.reply_to_message:
        return await message.reply("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ.")
    target = message.reply_to_message.from_user
    try:
        await message.chat.ban(user_id=target.id)
        await message.reply(f"🚫 {target.mention_html()} ʙᴀɴɴᴇᴅ.")
    except Exception as e:
        await message.reply(f"❌ ғᴀɪʟᴇᴅ: {e}")


@router.message(Command("unban"))
async def cmd_unban(message: Message):
    if not is_admin(message.from_user.id):
        return
    if not message.reply_to_message:
        return await message.reply("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ.")
    target = message.reply_to_message.from_user
    try:
        await message.chat.unban(user_id=target.id)
        await message.reply(f"✅ {target.mention_html()} ᴜɴʙᴀɴɴᴇᴅ.")
    except Exception as e:
        await message.reply(f"❌ ғᴀɪʟᴇᴅ: {e}")


# ─── GROUP SETTINGS ───
@router.message(Command("settings"))
async def cmd_settings(message: Message):
    if message.chat.type == "private":
        await message.reply("ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs ᴏɴʟʏ.")
        return
    if not is_admin(message.from_user.id):
        await message.reply("❌ ᴀᴅᴍɪɴs ᴏɴʟʏ.")
        return
    await get_or_create_group(message.chat.id)
    w = await get_group_setting(message.chat.id, "welcome_enabled")
    g = await get_group_setting(message.chat.id, "goodbye_enabled")
    a = await get_group_setting(message.chat.id, "antilink")
    text = (
        f"⚙️ <b>ɢʀᴏᴜᴘ sᴇᴛᴛɪɴɢs</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👋 ᴡᴇʟᴄᴏᴍᴇ: {'✅ ᴏɴ' if w else '❌ ᴏғғ'}\n"
        f"👋 ɢᴏᴏᴅʙʏᴇ: {'✅ ᴏɴ' if g else '❌ ᴏғғ'}\n"
        f"🔗 ᴀɴᴛɪʟɪɴᴋ: {'✅ ᴏɴ' if a else '❌ ᴏғғ'}"
    )
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 ᴛᴏɢɢʟᴇ ᴡᴇʟᴄᴏᴍᴇ", callback_data="grp:toggle:welcome_enabled")],
        [InlineKeyboardButton(text="🔄 ᴛᴏɢɢʟᴇ ɢᴏᴏᴅʙʏᴇ", callback_data="grp:toggle:goodbye_enabled")],
        [InlineKeyboardButton(text="🔄 ᴛᴏɢɢʟᴇ ᴀɴᴛɪʟɪɴᴋ", callback_data="grp:toggle:antilink")],
    ])
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("grp:toggle:"))
async def grp_toggle(cb: CallbackQuery):
    if not is_admin(cb.from_user.id):
        await cb.answer("ᴀᴅᴍɪɴs ᴏɴʟʏ", show_alert=True)
        return
    setting = cb.data.split(":")[2]
    await toggle_group_setting(cb.message.chat.id, setting)
    await cb.answer(f"✅ {setting} ᴛᴏɢɢʟᴇᴅ!")
