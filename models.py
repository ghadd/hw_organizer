from peewee import *
from playhouse.sqlite_ext import JSONField

from consts import Filter

db = SqliteDatabase('database.sqlite')


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    uid = IntegerField(unique=True)
    state = IntegerField(default=0)
    first_name = CharField()
    tasks = JSONField(default={})
    current_filters = JSONField(default={})

    @staticmethod
    def set_state(user, state):
        User.update(
            state=state
        ).where(
            User.uid == user.id
        ).execute()

    @staticmethod
    def get_state(user):
        return User.get(uid=user.id).state

    @staticmethod
    def get_users_tasks(user, *args):
        usr = User.get(User.uid == user.id)
        tasks = [Task.get(task_id) for task_id in usr.tasks]
        tasks = list(filter(lambda task: task.deadline, tasks))

        if Filter.ALL in args:
            return sorted(tasks, key=lambda task: task.deadline)

        if not (Filter.PRIVATE in args and Filter.SHARED in args):
            if Filter.PRIVATE in args:
                tasks = list(filter(lambda task: task.is_private, tasks))
            elif Filter.SHARED in args:
                tasks = list(filter(lambda task: not task.is_private, tasks))

        if not (Filter.DONE in args and Filter.UNDONE in args):
            if Filter.DONE in args:
                tasks = list(filter(lambda task: usr.id in task.done_by, tasks))
            elif Filter.UNDONE in args:
                tasks = list(filter(lambda task: usr.id not in task.done_by, tasks))

        return sorted(tasks, key=lambda task: task.deadline)

    @staticmethod
    def get_users_none_deadline_task(user):
        usr = User.get(User.uid == user.id)
        tasks = [Task.get(task_id) for task_id in usr.tasks]
        tasks = list(filter(lambda task: not task.deadline, tasks))

        return tasks[0]


class Group(BaseModel):
    users = JSONField(default={})


class Task(BaseModel):
    content = CharField()
    is_private = BooleanField(default=True)
    deadline = DateField(null=True)
    done_by = JSONField(default=[])
