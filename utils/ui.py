from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
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
    if msg is None:
        return

    has_media = bool(
        msg.photo or msg.video or msg.document
        or msg.animation or msg.audio
    )

    try:
        if has_media:
            await msg.edit_caption(caption=text, reply_markup=reply_markup)
        else:
            await msg.edit_text(text=text, reply_markup=reply_markup)
    except TelegramBadRequest as e:
        err = str(e).lower()

        # Same content — user clicked same button twice, ignore
        if "not modified" in err:
            return

        # Try the other method (in case detection failed)
        try:
            if has_media:
                await msg.edit_text(text=text, reply_markup=reply_markup)
            else:
                await msg.edit_caption(caption=text, reply_markup=reply_markup)
            return
        except Exception:
            pass

        # Last resort: delete old + send new
        try:
            await msg.delete()
        except Exception:
            pass

        try:
            await msg.answer(text, reply_markup=reply_markup)
        except Exception:
            pass


async def smart_send(
    message: Message,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
    disable_preview: bool = True,
):
    """
    Send a text message safely with optional link preview disabling.
    """
    from aiogram.types import LinkPreviewOptions

    kwargs = {"reply_markup": reply_markup}
    if disable_preview:
        kwargs["link_preview_options"] = LinkPreviewOptions(is_disabled=True)

    try:
        await message.answer(text, **kwargs)
    except Exception:
        try:
            await message.answer(text, reply_markup=reply_markup)
        except Exception:
            pass
