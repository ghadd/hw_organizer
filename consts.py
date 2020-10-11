class State:
    DEFAULT = 0
    PRIVATE_TASK = 1
    SHARED_TASK = 2
    DEADLINE = 3


class Filter:
    PRIVATE = 10
    SHARED = 20
    DONE = 30
    UNDONE = 40

    ALL = [PRIVATE, SHARED, DONE, UNDONE]