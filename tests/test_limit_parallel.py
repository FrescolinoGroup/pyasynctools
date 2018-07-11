"""
Tests for the ``limit_parallel`` decorator.
"""

import asyncio

import pytest

from fsc.async_tools import limit_parallel


@pytest.fixture
def count_coro():
    """
    Returns a coroutine function that returns the number of other instances
    that are currently running.
    """
    count = 0

    async def inner():  # pylint: disable=missing-docstring
        nonlocal count
        res = count
        count += 1
        await asyncio.sleep(0.)
        count -= 1
        return res

    return inner


def get_max_count(coro_func, loop, num_calls=100):
    """
    Get the maximum result amongst a number of calls to a given coroutine function.
    """
    return max(
        loop.run_until_complete(
            asyncio.gather(
                *[
                    asyncio.ensure_future(coro_func())
                    for _ in range(num_calls)
                ]
            )
        )
    )


@pytest.mark.parametrize('max_num_parallel', [1, 5, 20])
def test_limit_parallel(count_coro, max_num_parallel):  # pylint: disable=redefined-outer-name
    """
    Test the limit_parallel decorator by checking that the number of parallel
    calls does not exceed the maximum.
    """
    loop = asyncio.get_event_loop()
    assert get_max_count(count_coro, loop) > 10
    limited_coro = limit_parallel(max_num_parallel)(count_coro)
    assert get_max_count(limited_coro, loop) < max_num_parallel
