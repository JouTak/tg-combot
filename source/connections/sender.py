import html
import time
from collections import defaultdict, deque

import requests
from telebot.apihelper import ApiException

from source.app_logging import logger
from source.connections.bot_factory import bot


def _fmt_duration(seconds: float) -> str:
    if seconds < 1:
        return f"{int(round(seconds * 1000))} ms"
    if seconds < 60:
        return f"{seconds:.2f} s"
    m, s = divmod(int(round(seconds)), 60)
    return f"{m}m {s}s"


class TokenBucket:
    def __init__(self, max_calls: int, period: float):
        self.max_calls = max_calls
        self.period = period
        self.calls = deque()

    def wait(self):
        now = time.time()
        while self.calls and self.calls[0] <= now - self.period:
            self.calls.popleft()
        if len(self.calls) >= self.max_calls:
            sleep_time = self.period - (now - self.calls[0])
            if sleep_time > 0:
                logger.debug(f"Пауза {_fmt_duration(sleep_time)} (лимит {self.max_calls}/{int(self.period)}s)")
                time.sleep(sleep_time)
        self.calls.append(time.time())


# Telegram API limits are per-bot and per-chat; keep it conservative.
_global = TokenBucket(max_calls=25, period=1.0)
_per_chat = defaultdict(lambda: TokenBucket(max_calls=1, period=0.7))


def _auto_html(text: str | None) -> str:
    # minimal, predictable: escape all
    return html.escape(text or "", quote=False)


def send_message_limited(chat_id: int, text: str, **kwargs):
    """Wrapper for bot.send_message with basic rate limiting + HTML-safe text."""
    _global.wait()
    _per_chat[chat_id].wait()

    safe_text = _auto_html(text)
    kwargs.pop("parse_mode", None)
    kwargs["parse_mode"] = "HTML"

    try:
        return bot.send_message(chat_id, safe_text, **kwargs)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        logger.warning(
            f"Не смог отправить сообщение в chat_id={chat_id}: сеть недоступна "
            f"({'таймаут' if isinstance(e, requests.exceptions.Timeout) else 'нет соединения'})."
        )
        return None
    except ApiException as e:
        logger.warning(f"Ошибка Telegram API при отправке в chat_id={chat_id}: {e}")
        return None


def send_photo_limited(chat_id: int, photo_path: str, caption: str | None = None, **kwargs):
    _global.wait()
    _per_chat[chat_id].wait()

    safe_caption = _auto_html(caption)
    kwargs.pop("parse_mode", None)
    kwargs["parse_mode"] = "HTML"

    try:
        with open(photo_path, "rb") as f:
            return bot.send_photo(chat_id, f, caption=safe_caption, **kwargs)
    except FileNotFoundError:
        logger.warning(f"Photo not found: {photo_path}")
        return None
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        logger.warning(
            f"Не смог отправить фото в chat_id={chat_id}: сеть недоступна "
            f"({'таймаут' if isinstance(e, requests.exceptions.Timeout) else 'нет соединения'})."
        )
        return None
    except ApiException as e:
        logger.warning(f"Ошибка Telegram API при отправке фото в chat_id={chat_id}: {e}")
        return None
