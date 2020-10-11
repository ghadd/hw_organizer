from models import User


def reg_user(user):
    if not User.get_or_none(User.uid == user.id):
        User.create(
            uid=user.id,
            first_name=user.first_name
        )
        return True
    return False


def clear_cb(bot, cb):
    bot.answer_callback_query(cb.id)
    bot.delete_message(cb.from_user.id, cb.message.message_id)