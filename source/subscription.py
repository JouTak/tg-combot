from __future__ import annotations

from telebot.apihelper import ApiException
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from source.app_logging import logger
from source.config import CHANNEL_ID, CHANNEL_URL, SUBSCRIPTION_GATE_ENABLED, SUBSCRIPTION_PHOTO_PATH
from source.connections.bot_factory import bot
from source.connections.sender import send_message_limited, send_photo_limited




COMMUNITY_LINK = "https://itmocraft"

ALLOWED_STATUSES = {"member", "administrator", "creator"}


def is_enabled() -> bool:
    return SUBSCRIPTION_GATE_ENABLED and bool(CHANNEL_ID) and bool(CHANNEL_URL)


def subscription_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text="🔗 Перейти на наш канал любителей майнкрафта", url=CHANNEL_URL))
    kb.add(InlineKeyboardButton(text="✅ Я подписался!", callback_data="check_subscription"))
    return kb


def check_subscription(user_id: int) -> bool:
    if not is_enabled():
        return True
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        status = getattr(member, "status", None)
        return status in ALLOWED_STATUSES
    except ApiException as e:
        logger.warning(f"get_chat_member failed: {e}")
        return False
    except Exception as e:
        logger.warning(f"check_subscription error: {e}")
        return False


def send_gate(chat_id: int, user_id: int | None = None, message_thread_id: int | None = None):
    kb = subscription_keyboard()
    caption = "Просим подписаться на наш тг-канал! Никакого спама, только обсуждение обновлений и анонсы наших событий. После этого откроется доступ ко всем нужным материалам"
    if SUBSCRIPTION_PHOTO_PATH:
        sent = send_photo_limited(
            chat_id,
            SUBSCRIPTION_PHOTO_PATH,
            caption=caption,
            reply_markup=kb,
            message_thread_id=message_thread_id,
        )
        if sent is not None:
            return sent
    return send_message_limited(chat_id, caption, reply_markup=kb, message_thread_id=message_thread_id)


def ensure_subscribed(chat_id: int, user_id: int, message_thread_id: int | None = None) -> bool:
    if check_subscription(user_id):
        return True
    send_gate(chat_id, user_id=user_id, message_thread_id=message_thread_id)
    return False


def after_subscription(chat_id: int, message_thread_id: int | None = None):
    send_message_limited(chat_id, "✅ Подписка подтверждена. Пропиши /start", message_thread_id=message_thread_id)
