"""
utils/clone_middleware.py — Block clone bot updates when the clone owner
has left one of the required chats.

This middleware is attached ONLY to clone-bot dispatchers (not the main bot).
The main bot always runs regardless of its admins' membership.
"""

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Update, Message, CallbackQuery

from utils import clone_manager


BLOCK_TEXT = (
    "🚫 <b>ᴄʟᴏɴᴇ ʙᴏᴛ ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ ᴅɪꜱᴀʙʟᴇᴅ</b>\n"
    "━━━━━━━━━━━━━━━━━━━━━\n\n"
    "ᴛʜᴇ ᴏᴡɴᴇʀ ᴏꜰ ᴛʜɪꜱ ᴄʟᴏɴᴇ ʙᴏᴛ ʜᴀꜱ ʟᴇꜰᴛ ᴀ ʀᴇQᴜɪʀᴇᴅ\n"
    "ᴄʜᴀɴɴᴇʟ ᴏʀ ɢʀᴏᴜᴘ.\n\n"
    "🔁 ᴛʜᴇ ʙᴏᴛ ᴡɪʟʟ ʀᴇꜱᴜᴍᴇ ᴏɴᴄᴇ ᴛʜᴇ ᴏᴡɴᴇʀ ʀᴇᴊᴏɪɴꜱ\n"
    "ᴀʟʟ ʀᴇQᴜɪʀᴇᴅ ᴄʜᴀᴛꜱ."
)


class CloneAccessMiddleware(BaseMiddleware):
    """
    Attached to each clone dispatcher.
    Blocks updates if the clone owner is not in all required chats.
    """

    def __init__(self, clone_id: int):
        self.clone_id = clone_id

    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        # Fast in-memory check
        if not clone_manager.is_clone_allowed(self.clone_id):
            # Reply with the block message (only once per update)
            try:
                if isinstance(event, Message):
                    await event.answer(BLOCK_TEXT)
                elif isinstance(event, CallbackQuery):
                    await event.answer(
                        "🚫 ᴄʟᴏɴᴇ ʙᴏᴛ ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ ᴅɪꜱᴀʙʟᴇᴅ",
                        show_alert=True,
                    )
            except Exception:
                pass
            return  # 🚫 do not process the update

        return await handler(event, data)
