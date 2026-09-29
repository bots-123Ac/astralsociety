from functools import wraps
from aiogram.types import Message

DM_ONLY_MSG = "📈⚠️ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴡᴏʀᴋs ᴏɴʟʏ ɪɴ ᴀsᴛʀᴀʟ ᴇᴍᴘɪʀᴇ ᴅᴍ 🚀"


def dm_only(func):
    """Decorator: only allow command in private chat."""
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        if message.chat.type != "private":
            try:
                await message.reply(DM_ONLY_MSG)
            except Exception:
                pass
            return
        return await func(message, *args, **kwargs)
    return wrapper
