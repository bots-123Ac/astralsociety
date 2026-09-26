from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from aiogram.exceptions import TelegramBadRequest


async def smart_edit(
    callback: CallbackQuery,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
):
    """
    Safely edit a callback message — handles both photo (edit_caption)
    and text (edit_text) messages.
    Falls back to delete + resend if editing is not possible.
    """
    msg = callback.message
    try:
        # If message has media — edit caption instead
        if msg.photo or msg.video or msg.document or msg.animation or msg.audio:
            await msg.edit_caption(caption=text, reply_markup=reply_markup)
        else:
            await msg.edit_text(text=text, reply_markup=reply_markup)
    except TelegramBadRequest as e:
        err = str(e).lower()
        # "message is not modified" — user clicked same button again, ignore
        if "not modified" in err:
            return
        # Other errors — try delete + resend
        try:
            await msg.delete()
        except Exception:
            pass
        try:
            await msg.answer(text, reply_markup=reply_markup)
        except Exception:
            pass
