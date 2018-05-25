"""
Tests the PeriodicTask asynchronous context manager.
"""
import asyncio

import pytest

from fsc.async_tools import PeriodicTask


class CallCounter:
    """
    Callable used to count how many times the periodic task has been executed.
    """

    def __init__(self):
        self._count = 0

    def __call__(self):
        self._count += 1

    def __int__(self):
        return self._count


@pytest.mark.parametrize('sleep', [0.01, 0.02])
@pytest.mark.parametrize('delay', [0., 0.001, 0.002])
@pytest.mark.parametrize('run_on_exit', [True, False])
def test_periodic_task(sleep, delay, run_on_exit):
    """
    Test the PeriodicTask context manager.
    """
    count = CallCounter()
    loop = asyncio.get_event_loop()

    async def run():
        async with PeriodicTask(
            loop=loop, task_func=count, delay=delay, run_on_exit=run_on_exit
        ):
            await asyncio.sleep(sleep)

    loop.run_until_complete(run())
    # Give some margin for error since scheduling is not immediate.
    target_count = 1 * run_on_exit + sleep / (2 * (delay + 0.001))
    assert int(count) >= target_count
