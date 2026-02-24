from telebot.types import CallbackQuery

from source.connections.bot_factory import bot
from source.subscription import after_subscription, check_subscription, send_gate
from source.storage.user_store import touch_user


@bot.callback_query_handler(func=lambda c: (getattr(c, "data", "") or "") == "check_subscription")
def check_subscription_callback(c: CallbackQuery):
    msg = getattr(c, "message", None)
    if not msg:
        return
    user = getattr(c, "from_user", None)
    if not user:
        return

    touch_user(user, chat_id=msg.chat.id)

    chat_id = msg.chat.id
    thread_id = getattr(msg, "message_thread_id", None)

    ok = check_subscription(user.id)
    if ok:
        try:
            bot.delete_message(chat_id, msg.message_id)
        except Exception:
            pass
        after_subscription(chat_id, user_id=user.id, message_thread_id=thread_id)
        try:
            bot.answer_callback_query(c.id, text="✅ Ок")
        except Exception:
            pass
        return

    send_gate(chat_id, user_id=user.id, message_thread_id=thread_id)
    try:
        bot.answer_callback_query(c.id, text="❌ Не вижу подписку")
    except Exception:
        pass
