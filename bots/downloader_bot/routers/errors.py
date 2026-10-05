from html import escape

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from downloader_bot.infra.backend import BackendUnavailable


class CommandErrorMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        try:
            result = await handler(event, data)
        except (ValueError, BackendUnavailable) as exc:
            if isinstance(exc, BackendUnavailable) and exc.retryable:
                raise
            if isinstance(event, CallbackQuery):
                await event.answer(str(exc)[:200], show_alert=True)
            elif isinstance(event, Message):
                await event.answer(escape(str(exc)[:500]))
            return None
        return result
