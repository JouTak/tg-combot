from __future__ import annotations

from telebot.apihelper import ApiException
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from source.app_logging import logger
from source.config import BOT_URL, CHANNEL_ID, CHANNEL_URL, SUBSCRIPTION_GATE_ENABLED, SUBSCRIPTION_PHOTO_PATH
from source.connections.bot_factory import bot
from source.connections.sender import send_message_limited, send_photo_limited
from source.storage.user_store import mark_gate_shown, mark_materials_sent, mark_subscription_verified




COMMUNITY_LINK = (f"Будем так же рады вашим подпискам на наш тикток @joutaksmp!"
                  f"\nМатериалы:\nСкин Пети Гуменника вместе с инструкцией - cloud.joutak.ru/s/6b2NxK37GP2H9mm"
                  f"\n"
                  f"\nВ случае возникновения вопросов можешь писать создателю проекта - @enderdissa")

ALLOWED_STATUSES = {"member", "administrator", "creator"}


def is_enabled() -> bool:
    return SUBSCRIPTION_GATE_ENABLED and bool(CHANNEL_ID) and bool(CHANNEL_URL)


def subscription_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text="🔗 Перейти на канал ITMOcraft", url=CHANNEL_URL))
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
    if user_id is not None:
        mark_gate_shown(user_id)
    kb = subscription_keyboard()
    caption = ("Просим подписаться на наш тг-канал любителей майнкрафта!\n"
               "Никакого спама, только обсуждение обновлений и анонсы наших событий. После этого откроется доступ ко всем интересующим материалам")
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


def after_subscription(chat_id: int, user_id: int | None = None, message_thread_id: int | None = None):
    if user_id is not None:
        mark_subscription_verified(user_id)
        mark_materials_sent(user_id)
    lines = [
        "✅ Подписка подтверждена!",
        COMMUNITY_LINK
    ]
    if BOT_URL:
        lines += ["", "Ссылка на бота: " + BOT_URL]
    send_message_limited(chat_id, "\n".join(lines), message_thread_id=message_thread_id)
