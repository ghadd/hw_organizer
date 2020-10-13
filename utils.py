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


def get_task_stub(task):
    title = task.content.split('\n')[0]
    body = '\n'.join(task.content.split('\n')[1:])
    body_stub = f'\n<i>{body}</i>\n' if body else ''

    stub = f"<b>{title}</b>\n{body_stub}\n<b>Deadline:</b> <i>{task.deadline.strftime('%d.%m.%Y')}</i>\n" \
           f"<b>Type:</b> <i>{'Private' if task.is_private else 'Shared'}</i>"
    return stub
