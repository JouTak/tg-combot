from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from source.app_logging import logger
from source.connections.bot_factory import bot
from source.connections.sender import send_message_limited


@bot.message_handler(commands=["start", "help"])
def start_handler(message):
    chat_id = message.chat.id
    send_message_limited(
        chat_id,
        "Привет! Я шаблон бота.\n\n"
        "Команды:\n"
        "/ping — проверка связи\n"
        "/demo — пример кнопки (callback)",
        message_thread_id=getattr(message, "message_thread_id", None),
    )


@bot.message_handler(commands=["ping"])
def ping_handler(message):
    chat_id = message.chat.id
    send_message_limited(chat_id, "pong", message_thread_id=getattr(message, "message_thread_id", None))


@bot.message_handler(commands=["demo"])
def demo_handler(message):
    chat_id = message.chat.id
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text="Нажми меня", callback_data="demo:hello"))
    send_message_limited(chat_id, "Демо-кнопка:", reply_markup=kb, message_thread_id=getattr(message, "message_thread_id", None))


@bot.message_handler(commands=["whereami"])
def whereami_handler(message):
    # удобная утилита для дебага/настройки
    send_message_limited(
        message.chat.id,
        f"chat_id={message.chat.id}\nmessage_thread_id={getattr(message, 'message_thread_id', None)}",
        message_thread_id=getattr(message, "message_thread_id", None),
    )


@bot.message_handler(func=lambda msg: True, content_types=["text"])
def fallback_text(message):
    # Минимальный fallback, чтобы было видно, что бот жив.
    logger.info(f"Unhandled text from chat_id={message.chat.id}: {message.text!r}")
    # В проде обычно лучше молчать или отвечать только в ЛС — тут оставим мягкий echo.
    send_message_limited(message.chat.id, f"Ты написал: {message.text}", message_thread_id=getattr(message, "message_thread_id", None))
