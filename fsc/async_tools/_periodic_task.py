"""
Defines an asynchronous context manager for running periodic tasks.
"""

import asyncio

from fsc.export import export


@export
class PeriodicTask:
    """Asynchronous context manager that periodically runs a given function.

    Args:
        loop (EventLoop): The event loop on which the tasks are executed. Uses :func:`asyncio.get_event_loop()` if no event loop is specified.
        task_func (Callable): The function which is executed. It cannot take any arguments, and must not be a coroutine.
        delay (float): The minimum time between running two calls to the function.
        run_on_exit (bool): Determines if the function should be run again when exiting the context manager.
    """

    def __init__(self, task_func, *, loop=None, delay=1., run_on_exit=True):
        if loop is None:
            self._loop = asyncio.get_event_loop()
        else:
            self._loop = loop
        self._task_func = task_func
        self._delay = float(delay)
        self._run_on_exit = run_on_exit
        self._task_loop_started = False

    async def __aenter__(self):
        self._periodic_task = self._loop.create_task(self._task_loop())  # pylint: disable=attribute-defined-outside-init

    async def __aexit__(self, exc_type, exc_value, traceback):  # pylint: disable=missing-docstring
        while not self._task_loop_started:  # Make sure the periodic task was started
            await asyncio.sleep(0.)
        self._task_loop_started = False
        self._periodic_task.cancel()
        await self._periodic_task
        del self._periodic_task

    async def _task_loop(self):
        """
        Runs the periodic task until cancelled.
        """
        self._task_loop_started = True
        try:
            while True:
                self._task_func()
                await asyncio.sleep(self._delay)
        except asyncio.CancelledError:
            if self._run_on_exit:
                self._task_func()
