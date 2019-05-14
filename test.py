#!/usr/bin/env python3
import asyncio as aio
import unittest as ut

from aio_task_bound_context import *


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
class TestContextDefaults(TaskBoundContext):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class TestTaskBoundContext(ut.TestCase):
    def setUp(self):
        self.loop = aio.get_event_loop()
        set_task_factory(loop = self.loop)
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

    def test_single_task_default_value(self):
        """ Single task gets context stack and uses the context as value """
        self.loop.run_until_complete(self._test_single_task_default_value())
    async def _test_single_task_default_value(self):
        ctx_outer = TestContextDefaults('test value')
        with ctx_outer:
            self.assertEqual(TestContextDefaults.current(), ctx_outer)
            ctx_inner = TestContextDefaults('another value')
            with ctx_inner:
                self.assertEqual(TestContextDefaults.current(), ctx_inner)
            self.assertEqual(TestContextDefaults.current(), ctx_outer)

    def test_single_task_as_value(self):
        """ Context as value is the result of get_value """
        self.loop.run_until_complete(self._test_single_task_as_value())
    async def _test_single_task_as_value(self):
        with TestContext('test value') as value:
            self.assertEqual(value, 'test value')
            with TestContext('another value') as value:
                self.assertEqual(value, 'another value')

    def test_single_task_async_as_value(self):
        """ Context as value is the result of get_value """
        self.loop.run_until_complete(self._test_single_task_async_as_value())
    async def _test_single_task_async_as_value(self):
        async with ATestContext('test value') as value:
            self.assertEqual(value, 'test value')
            async with ATestContext('another value') as value:
                self.assertEqual(value, 'another value')

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
                await aio.sleep(0.2)
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
                await aio.sleep(0.2)
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
