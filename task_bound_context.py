import asyncio as aio

from functools import lru_cache, wraps


def alru_cache(func):
    has_value = False
    value = None

    @wraps(func)
    async def inner(*args, **kwargs):
        if not has_value:
            value = await func(*args, **kwargs)
        return value

    return inner


class TaskBoundContext(object):
    def get_value(self):
        raise NotImplementedError('Must override get_value')

    @classmethod
    def get_stack(cls):
        current_task = task = aio.Task.current_task()
        stack = None
        while task is not None:
            stack = task._ctx_stacks.get(cls, None)
            if stack is None or stack == []:
                task = task._ctx_parent
            else:
                if task != current_task:
                    stack = [stack[-1]]
                    current_task._ctx_stacks[cls] = stack
                break

        if stack is None:
            current_task._ctx_stacks[cls] = []

        return current_task._ctx_stacks[cls]

    @lru_cache()
    def _get_value_sync(self):
        return self.get_value()
    @alru_cache
    async def _get_value_async(self):
        return await self.get_value()

    def __enter__(self):
        self._do_enter(self._get_value_sync())
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._do_exit(self._get_value_sync())

    async def __aenter__(self):
        self._do_enter(await self._get_value_async())
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._do_exit(await self._get_value_async())

    def _do_enter(self, value):
        self.get_stack().append(value)
    def _do_exit(self, value):
        popped = self.get_stack().pop()
        assert popped == value

    @classmethod
    def current(cls):
        try:
            return cls.get_stack()[-1]
        except IndexError:
            raise ValueError('No context')


def wrap_task(task):
    setattr(task, '_ctx_parent', aio.Task.current_task())
    setattr(task, '_ctx_stacks', {})
    return task


def create_task_factory(task_factory = None, loop = None):
    if loop is None and task_factory is None:
        loop = aio.get_event_loop()
    if task_factory is None:
        task_factory = loop.get_task_factory()

    def inner(inner_loop, coro):
        if task_factory is None:
            task = aio.Task(coro, loop = inner_loop)
            return wrap_task(task)
        else:
            return wrap_task(task_factory(inner_loop, coro))

        return wrap_task(task)

    return inner
