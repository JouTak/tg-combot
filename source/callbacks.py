from telebot.types import CallbackQuery

from source.connections.bot_factory import bot
from source.connections.sender import send_message_limited


@bot.callback_query_handler(func=lambda c: bool(getattr(c, "data", "")) and c.data.startswith("demo:"))
def demo_callback(c: CallbackQuery):
    # demo:hello
    chat_id = c.message.chat.id
    payload = (c.data or "").split(":", 1)[1] if ":" in (c.data or "") else ""
    send_message_limited(chat_id, f"Callback получил: {payload}", message_thread_id=getattr(c.message, "message_thread_id", None))
    try:
        bot.answer_callback_query(c.id)
    except Exception:
        pass
