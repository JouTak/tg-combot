from source.connections.bot_factory import bot
from source.connections.sender import send_message_limited
from source.subscription import after_subscription, ensure_subscribed


@bot.message_handler(commands=["start", "help"])
def start_handler(message):
    if getattr(message.chat, "type", None) != "private":
        return
    user = getattr(message, "from_user", None)
    if not user:
        return
    if not ensure_subscribed(
        message.chat.id,
        user.id,
        message_thread_id=getattr(message, "message_thread_id", None),
    ):
        return
    after_subscription(message.chat.id, message_thread_id=getattr(message, "message_thread_id", None))


@bot.message_handler(func=lambda msg: True, content_types=["text"])
def fallback_text(message):
    if getattr(message.chat, "type", None) != "private":
        return
    send_message_limited(
        message.chat.id,
        "Нажми /start",
        message_thread_id=getattr(message, "message_thread_id", None),
    )
