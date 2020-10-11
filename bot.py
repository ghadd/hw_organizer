import datetime
import re

import telebot

import markups
import text
import utils
from consts import Filter, State
from models import User, Task
from utils import clear_cb

TOKEN = '1338218026:AAGbE9EfKG5IkLBISCzaSJrQG3uBdu1aLzg'
bot = telebot.TeleBot(TOKEN, threaded=False)

send = bot.send_message


@bot.message_handler(commands=['start'])
def start(msg):
    utils.reg_user(msg.from_user)
    menu(msg)


@bot.message_handler(commands=['menu'])
def menu(msg):
    send(msg.from_user.id, text.menu, reply_markup=markups.menu)


@bot.message_handler(func=lambda msg: User.get_state(msg.from_user) in [State.PRIVATE_TASK, State.SHARED_TASK])
def create_task(msg):
    task_content = msg.text
    task_mode = User.get_state(msg.from_user)
    task = Task.create(
        content=task_content,
        is_private=task_mode == State.PRIVATE_TASK,
    )
    User.set_state(msg.from_user, State.DEADLINE)
    tasks = User.get_users_tasks(msg.from_user, Filter.ALL)
    User.update(
        tasks=[task.id for task in tasks] + [task.id]
    ).where(
        User.uid == msg.from_user.id
    ).execute()

    send(msg.from_user.id, text.task_added, reply_markup=markups.get_date_helper())


@bot.message_handler(func=lambda msg: User.get_state(msg.from_user) in [State.DEADLINE])
def set_task_deadline(msg):
    try:
        deadline = datetime.datetime.strptime(msg.text, '%d.%m.%Y')
        task = User.get_users_none_deadline_task(msg.from_user)
        Task.update(
            deadline=deadline
        ).where(
            Task.id == task.id
        ).execute()
        send(msg.from_user.id, "Updated deadline!", reply_markup=markups.REMOVE_KB)

        User.set_state(msg.from_user, State.DEFAULT)
        menu(msg)

    except ValueError:
        send(msg.from_user.id, text.INVALID_DATE)


@bot.callback_query_handler(func=lambda cb: cb.data in text.task_callbacks)
def handle_tasks(cb):
    if cb.data == text.ADD_TASK:
        send(cb.from_user.id, text.task_mode, reply_markup=markups.task_mode)
        clear_cb(bot, cb)
    elif cb.data == text.PRIVATE_TASK:
        send(cb.from_user.id, text.add_private_task, reply_markup=markups.cancel)
        User.set_state(cb.from_user, State.PRIVATE_TASK)
        clear_cb(bot, cb)
    elif cb.data == text.SHARED_TASK:
        send(cb.from_user.id, text.add_shared_task, reply_markup=markups.cancel)
        User.set_state(cb.from_user, State.SHARED_TASK)
        clear_cb(bot, cb)
    elif cb.data == text.CANCEL:
        User.set_state(cb.from_user, State.DEFAULT)
        clear_cb(bot, cb)
        menu(cb)  # nah


@bot.callback_query_handler(func=lambda cb: cb.data in text.navigate_callbacks)
def handle_navigate(cb):
    if cb.data == text.NAV_FILTERS:
        send(cb.from_user.id, 'filters', reply_markup=markups.navigate_filter)
        clear_cb(bot, cb)


@bot.callback_query_handler(func=lambda cb: cb.data in text.navigate_filters)
def handle_navigate(cb):
    if cb.data == text.APPLY:
        filters = markups.get_filters(cb.message.json['reply_markup']['inline_keyboard'])
        User.update(
            current_filters=filters
        ).where(
            User.uid == cb.from_user.id
        ).execute()

        tasks = User.get_users_tasks(
            cb.from_user,
            *filters
        )
        ind = 0
        send(cb.from_user.id, tasks[ind].content, reply_markup=markups.navigate(tasks[ind], ind))
        clear_cb(bot, cb)
    else:
        idx = text.navigate_filters.index(cb.data)
        old_markup = telebot.types.InlineKeyboardMarkup()
        old_markup.keyboard = cb.message.json['reply_markup']['inline_keyboard']
        new_markup = markups.update(old_markup, idx)

        bot.edit_message_reply_markup(
            cb.from_user.id,
            cb.message.message_id,
            reply_markup=new_markup
        )
        bot.answer_callback_query(cb.id)


@bot.callback_query_handler(func=lambda cb: re.search(r'mark_as_done|^([+-]?[1-9]\d*|0)$', cb.data))
def nav_controls_handler(cb):
    try:
        idx = int(cb.data)
        user = User.get(User.uid == cb.from_user.id)
        tasks = User.get_users_tasks(cb.from_user, user.current_filters)
        if idx < 0 or idx >= len(tasks):
            bot.answer_callback_query(cb.id, "No more tasks there.")
        else:
            bot.edit_message_text(
                tasks[idx].content,
                cb.from_user.id,
                cb.message.message_id
            )
            bot.edit_message_reply_markup(
                cb.from_user.id,
                cb.message.message_id,
                reply_markup=markups.navigate(tasks[idx], idx)
            )
            bot.answer_callback_query(cb.id)
    except ValueError:
        task_id = int(cb.data.split('-')[1])
        task = Task.get(task_id)
        task.done_by.append(User.get(User.uid == cb.from_user.id).id)
        task.save()


if __name__ == '__main__':
    bot.polling(none_stop=True)