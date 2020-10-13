import datetime

from telebot.types import InlineKeyboardMarkup as Brd, InlineKeyboardButton as Btn
from telebot.types import ReplyKeyboardMarkup as KBrd, ReplyKeyboardRemove

import text
from consts import Filter
from models import User

menu = Brd()
menu.row(Btn("Add task", callback_data='add_task'))
menu.row(Btn("Navigate tasks", callback_data='navigate_filters'))
menu.add(Btn("Create Group", callback_data='create_group'))
menu.add(Btn("Join Group", callback_data='join_group'))

task_mode = Brd()
task_mode.add(Btn("Private Task", callback_data='private_task'))
task_mode.add(Btn("Shared Task", callback_data='shared_task'))
task_mode.add(Btn("Cancel", callback_data='cancel'))

cancel = Brd()
cancel.add(Btn("Cancel", callback_data='cancel'))


def navigate(user, task, ind):
    usr = User.get(User.uid == user.id)
    addon = 'un' if usr.id in task.done_by else ''

    nav = Brd()
    # make gray if no way
    nav.add(Btn('Prev', callback_data=f'{ind - 1}'),
            Btn(f'Mark as {addon}done', callback_data=f"mark_as_{addon}done-{task.id}"),
            Btn('Next', callback_data=f'{ind + 1}'))
    return nav


navigate_filter = Brd()
navigate_filter.row(Btn('Private', callback_data='private_filter'), Btn('Shared', callback_data='shared_filter'))
navigate_filter.row(Btn('Done', callback_data='done_filter'), Btn('Undone', callback_data='undone_filter'))
navigate_filter.row(Btn('Apply', callback_data='apply'))
navigate_filter.row(Btn('Back to menu', callback_data='cancel'))


def get_date_helper():
    dates = []
    for i in range(1, 8):
        date = datetime.date.today() + datetime.timedelta(days=i)
        label = date.strftime('%d.%m.%Y')
        dates.append(label)

    return KBrd().row(dates[0]).add(*dates[1:])


REMOVE_KB = ReplyKeyboardRemove()


def update(markup, idx):
    row = idx // 2
    col = idx % 2
    markup.keyboard[row][col]['text'] = markup.keyboard[row][col]['text'] + '✅' \
        if '✅' not in markup.keyboard[row][col]['text'] \
        else markup.keyboard[row][col]['text'].replace('✅', '')
    return markup


def get_filters(inline_kb):
    filters = []
    flat = [item for sublist in inline_kb for item in sublist][:-1]
    for f in flat:
        if f['callback_data'] == text.PRIVATE_FILTER and '✅' in f['text']:
            filters.append(Filter.PRIVATE)
        elif f['callback_data'] == text.SHARED_FILTER and '✅' in f['text']:
            filters.append(Filter.SHARED)
        elif f['callback_data'] == text.DONE_FILTER and '✅' in f['text']:
            filters.append(Filter.DONE)
        elif f['callback_data'] == text.UNDONE_FILTER and '✅' in f['text']:
            filters.append(Filter.UNDONE)

    return filters


back = Brd()
back.add(Btn('Back', callback_data='back'))
