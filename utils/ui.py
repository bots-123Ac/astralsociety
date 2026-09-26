from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from aiogram.exceptions import TelegramBadRequest


async def smart_edit(
    callback: CallbackQuery,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
):
    """Safely edit caption/text depending on message type."""
    msg = callback.message
    try:
        if msg.photo or msg.video or msg.document or msg.animation or msg.audio:
            await msg.edit_caption(caption=text, reply_markup=reply_markup)
        else:
            await msg.edit_text(text=text, reply_markup=reply_markup)
    except TelegramBadRequest as e:
        err = str(e).lower()
        if "not modified" in err:
            return
        try:
            await msg.delete()
        except Exception:
            pass
        try:
            await msg.answer(text, reply_markup=reply_markup)
        except Exception:
            pass
