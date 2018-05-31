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


@pytest.fixture(params=[None, asyncio.get_event_loop()])
def loop(request):
    """
    Fixture that creates the 'loop' argument.
    """
    return request.param


@pytest.fixture
def run_future(loop):  # pylint: disable=redefined-outer-name
    """
    Fixture to run a future in the event loop.
    """

    def inner(fut):  # pylint: disable=missing-docstring
        if loop is None:
            curr_loop = asyncio.get_event_loop()
        else:
            curr_loop = loop
        curr_loop.run_until_complete(fut)

    return inner


@pytest.mark.parametrize('sleep', [0.01, 0.02])
@pytest.mark.parametrize('delay', [0., 0.001, 0.002])
@pytest.mark.parametrize('run_on_exit', [True, False])
def test_periodic_task(sleep, loop, run_future, delay, run_on_exit):  # pylint: disable=redefined-outer-name
    """
    Test the PeriodicTask context manager.
    """
    count = CallCounter()

    async def run():
        async with PeriodicTask(
            count, loop=loop, delay=delay, run_on_exit=run_on_exit
        ):
            await asyncio.sleep(sleep)

    run_future(run())
    # Give some margin for error since scheduling is not immediate.
    target_count = 1 * run_on_exit + sleep / (2 * (delay + 0.001))
    assert int(count) >= target_count


def test_multiple_entries(run_future):  # pylint: disable=redefined-outer-name
    """
    Test that the PeriodicTask can be used multiple times as a context manager.
    """
    count = CallCounter()

    async def run():  # pylint: disable=missing-docstring
        periodic_task = PeriodicTask(count, delay=0.)
        async with periodic_task:
            await asyncio.sleep(0.)
        assert int(count) > 0
        count._count = 0  # pylint: disable=protected-access
        async with periodic_task:
            await asyncio.sleep(0.)
        assert int(count) > 0

    run_future(run())


def test_run_error(run_future):  # pylint: disable=redefined-outer-name
    """
    Test that errors are properly propagated.
    """

    def error_func():
        raise ValueError

    async def run():
        async with PeriodicTask(error_func, delay=0.):
            await asyncio.sleep(0.1)

    with pytest.raises(ValueError):
        run_future(run())
