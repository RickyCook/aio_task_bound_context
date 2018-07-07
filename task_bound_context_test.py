#!/usr/bin/env python3
import asyncio as aio
import unittest as ut

from task_bound_context import *


class TestContext(TaskBoundContext):
    def __init__(self, value):
        self.value = value
    def get_value(self):
        return self.value
class ATestContext(TaskBoundContext):
    def __init__(self, value):
        self.value = value
    async def get_value(self):
        return self.value


class TestTaskBoundContext(ut.TestCase):
    def setUp(self):
        self.loop = aio.get_event_loop()
        self.loop.set_task_factory(create_task_factory(loop = self.loop))
    def tearDown(self):
        self.loop.set_task_factory(None)

    def test_single_task(self):
        """ Single task gets context stack that's pushed/popped correctly """
        self.loop.run_until_complete(self._test_single_task())
    async def _test_single_task(self):
        with TestContext('test value'):
            self.assertEqual(TestContext.current(), 'test value')
            with TestContext('another value'):
                self.assertEqual(TestContext.current(), 'another value')
            self.assertEqual(TestContext.current(), 'test value')

    def test_single_task_async(self):
        """ Test the async version of the context manager """
        self.loop.run_until_complete(self._test_single_task_async())
    async def _test_single_task_async(self):
        async with ATestContext('aio test value'):
            self.assertEqual(ATestContext.current(), 'aio test value')
            async with ATestContext('aio another value'):
                self.assertEqual(ATestContext.current(), 'aio another value')
            self.assertEqual(ATestContext.current(), 'aio test value')

    def test_single_task_no_context(self):
        """ Error correctly with no context """
        self.loop.run_until_complete(self._test_single_task_no_context())
    async def _test_single_task_no_context(self):
        with self.assertRaises(ValueError, msg = 'No context'):
            TestContext.current()

    def test_gathered_tasks(self):
        """ Multiple tasks get their own context """
        self.loop.run_until_complete(self._test_gathered_tasks())
    async def _test_gathered_tasks(self):
        async def func_a():
            with TestContext('gathered.a'):
                aio.sleep(0.2)
                self.assertEqual(TestContext.current(), 'gathered.a')
        async def func_b():
            with TestContext('gathered.b'):
                self.assertEqual(TestContext.current(), 'gathered.b')

        await aio.gather(func_a(), func_b())

    def test_gathered_tasks_hierarchy(self):
        """ Multiple tasks inherit their root context from parent """
        self.loop.run_until_complete(self._test_gathered_tasks())
    async def _test_gathered_tasks(self):
        async def func_a():
            self.assertEqual(TestContext.current(), 'gathered_h.outer')
            with TestContext('gathered_h.a'):
                aio.sleep(0.2)
                self.assertEqual(TestContext.current(), 'gathered_h.a')
            self.assertEqual(TestContext.current(), 'gathered_h.outer')
        async def func_b():
            self.assertEqual(TestContext.current(), 'gathered_h.outer')
            with TestContext('gathered_h.b'):
                self.assertEqual(TestContext.current(), 'gathered_h.b')
            self.assertEqual(TestContext.current(), 'gathered_h.outer')

        with TestContext('gathered_h.outer'):
            await aio.gather(func_a(), func_b())


if __name__ == '__main__':
    ut.main()
