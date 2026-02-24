from source.connections.bot_factory import bot
from source.subscription import after_subscription, ensure_subscribed
from source.storage.user_store import touch_user


@bot.message_handler(commands=["start", "help"])
def start_handler(message):
    if getattr(message.chat, "type", None) != "private":
        return
    user = getattr(message, "from_user", None)
    if not user:
        return
    touch_user(user, chat_id=message.chat.id)
    if not ensure_subscribed(
        message.chat.id,
        user.id,
        message_thread_id=getattr(message, "message_thread_id", None),
    ):
        return
    after_subscription(message.chat.id, user_id=user.id, message_thread_id=getattr(message, "message_thread_id", None))


@bot.message_handler(func=lambda msg: True, content_types=["text"])
def fallback_text(message):
    if getattr(message.chat, "type", None) != "private":
        return
    user = getattr(message, "from_user", None)
    if not user:
        return
    touch_user(user, chat_id=message.chat.id)
    if not ensure_subscribed(
        message.chat.id,
        user.id,
        message_thread_id=getattr(message, "message_thread_id", None),
    ):
        return
    after_subscription(message.chat.id, user_id=user.id, message_thread_id=getattr(message, "message_thread_id", None))
