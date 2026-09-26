from aiogram import Router, F
from aiogram.types import ChatMemberUpdated, Message
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER

from config import SUPPORT_GROUP_NAME, BOT_NAME

router = Router()


@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def welcome_new_member(event: ChatMemberUpdated):
    user = event.new_chat_member.user
    try:
        photos = await event.bot.get_user_profile_photos(user.id, limit=1)
        pfp_id = photos.photos[0][-1].file_id if photos.total_count else None
    except Exception:
        pfp_id = None

    try:
        chat_info = await event.bot.get_chat(user.id)
        bio = chat_info.bio or "вiσ ησт sєᴛ"
    except Exception:
        bio = "вiσ ησт sєᴛ"

    username = f"@{user.username}" if user.username else "ᴜsєʀηᴧᴍє ησт sєᴛ"
    mention = user.mention_html()
    members = await event.bot.get_chat_members_count(event.chat.id)

    text = (
        f"🌌 <b>ᴧ ηєᴡ sᴛᴧʀ єηᴛєʀєᴅ {SUPPORT_GROUP_NAME}</b> 🌌\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"✦ ηᴧϻє → {mention}\n"
        f"✦ ᴜsєʀηᴧϻє → {username}\n"
        f"✦ ᴜsєʀ iᴅ → <code>{user.id}</code>\n"
        f"✦ вiσ → {bio}\n"
        f"✦ ϻєϻвєʀs → {members}\n\n"
        f"🌸 sтᴧʏ нᴧᴩᴩʏ & єηᴊᴏʏ ʏᴏᴜʀ тɪᴍє! 🌸\n\n"
        f"🚀 ᴡєʟᴄᴏᴍє тᴏ {BOT_NAME}"
    )

    try:
        if pfp_id:
            await event.bot.send_photo(event.chat.id, photo=pfp_id, caption=text)
        else:
            await event.bot.send_message(event.chat.id, text)
    except Exception:
        pass


@router.chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))
async def goodbye_member(event: ChatMemberUpdated):
    user = event.new_chat_member.user
    text = (
        f"👋 <b>ɢσσᴅʙʏє!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{user.mention_html()} нᴧs ʟєғᴛ тнє ɢʀσᴜᴩ.\n\n"
        f"🌸 ᴡє'ʟʟ ϻiss ʏσᴜ!"
    )
    try:
        await event.bot.send_message(event.chat.id, text)
    except Exception:
        pass
