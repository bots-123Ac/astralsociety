import logging
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message, LinkPreviewOptions, ChatMemberUpdated,
)

from config import BOT_NAME, CREDIT_HTML
from keyboards.main_menu import main_menu_kb
from utils.database import get_or_create_user, register_group

router = Router()
logger = logging.getLogger(__name__)

NO_PREVIEW = LinkPreviewOptions(is_disabled=True)


def welcome_text(first_name: str) -> str:
    return (
        f"👋 ʜɪ, <b>{first_name}</b>!\n\n"
        f"ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ <b>{BOT_NAME}</b> 🌌\n\n"
        f"ʏᴏᴜʀ ᴀʟʟ-ɪɴ-ᴏɴᴇ ᴛᴇʟᴇɢʀᴀᴍ ᴄᴏᴍᴘᴀɴɪᴏɴ ғᴏʀ\n"
        f"ꜱᴛᴜᴅʏ, ɢᴀᴍᴇꜱ ᴀɴᴅ ᴍᴏʀᴇ.\n\n"
        f"ᴄʜᴏᴏꜱᴇ ᴀɴ ᴏᴘᴛɪᴏɴ ʙᴇʟᴏᴡ 👇\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"👨‍💻 {CREDIT_HTML}"
    )


# ═══════════════════════════════════════════════
# /start — DM + GC
# ═══════════════════════════════════════════════
@router.message(CommandStart())
async def cmd_start(message: Message):
    try:
        user = message.from_user
        await get_or_create_user(user.id, user.username, user.first_name)

        # ═══ Group me /start ═══
        if message.chat.type in ("group", "supergroup"):
            # Group ko register karo
            try:
                await register_group(message.chat.id, message.chat.title or "")
            except Exception as e:
                logger.warning(f"Group register failed: {e}")
            return

        # ═══ DM me /start ═══
        text = welcome_text(user.first_name)
        kb = main_menu_kb()

        # PFP try karo
        try:
            photos = await message.bot.get_user_profile_photos(user.id, limit=1)
            if photos.total_count > 0:
                file_id = photos.photos[0][-1].file_id
                await message.answer_photo(
                    photo=file_id,
                    caption=text,
                    reply_markup=kb,
                )
                return
        except Exception:
            pass

        await message.answer(
            text,
            reply_markup=kb,
            link_preview_options=NO_PREVIEW,
        )
    except Exception as e:
        logger.error(f"/start err: {e}")


# ═══════════════════════════════════════════════
# 🆕 BOT ADDED TO GROUP — Auto Register
# ═══════════════════════════════════════════════
@router.my_chat_member()
async def on_bot_chat_member(event: ChatMemberUpdated):
    """
    Fire jab bhi bot ka status change ho (add, remove, promote, demote).
    Isse hum group auto-register karte hain.
    """
    try:
        chat = event.chat
        if chat.type not in ("group", "supergroup"):
            return

        new_status = event.new_chat_member.status
        old_status = event.old_chat_member.status

        # ═══ Bot ko group me ADD kiya gaya ═══
        if (
            new_status in ("member", "administrator")
            and old_status in ("left", "kicked")
        ):
            await register_group(chat.id, chat.title or "")
            logger.info(f"✅ Group registered: {chat.title} ({chat.id})")
            try:
                await event.bot.send_message(
                    chat.id,
                    "🤖 <b>ᴛʜᴀɴᴋꜱ ꜰᴏʀ ᴀᴅᴅɪɴɢ ᴍᴇ!</b>\n\n"
                    "ᴜꜱᴇ /help ᴛᴏ ꜱᴇᴇ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅꜱ.\n"
                    "ᴜꜱᴇ /start ᴛᴏ ᴏᴩᴇɴ ᴛʜᴇ ᴍᴇɴᴜ."
                )
            except Exception:
                pass

        # ═══ Bot ko REMOVE kiya gaya ═══
        elif (
            new_status in ("left", "kicked")
            and old_status in ("member", "administrator")
        ):
            logger.info(f"❌ Bot removed from group: {chat.title} ({chat.id})")
            # Optional: delete from active_groups
            try:
                from utils.database import get_pool
                pool = await get_pool()
                await pool.execute(
                    "DELETE FROM active_groups WHERE chat_id = $1",
                    chat.id
                )
            except Exception:
                pass

    except Exception as e:
        logger.error(f"my_chat_member error: {e}")
