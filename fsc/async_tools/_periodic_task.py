"""
Defines an asynchronous context manager for running periodic tasks.
"""

import asyncio

from fsc.export import export


@export
class PeriodicTask:
    """Asynchronous context manager that periodically runs a given function.

    Args:
        loop (EventLoop): The event loop on which the tasks are executed.
        task_func (Callable): The function which is executed. It cannot take any arguments.
        delay (float): The minimum time between running two calls to the function.
    """

    def __init__(self, *, loop, task_func, delay=1.):
        self._loop = loop
        self._task_func = task_func
        self._delay = float(delay)

    async def __aenter__(self):
        self._periodic_task = self._loop.create_task(self._task_loop())  # pylint: disable=attribute-defined-outside-init
        await asyncio.sleep(0.)  # Allow the task loop to start.

    async def __aexit__(self, exc_type, exc_value, traceback):
        self._periodic_task.cancel()
        await self._periodic_task

    async def _task_loop(self):
        """
        Runs the periodic task until cancelled.
        """
        try:
            while True:
                self._task_func()
                await asyncio.sleep(self._delay)
        except asyncio.CancelledError:
            self._task_func()
