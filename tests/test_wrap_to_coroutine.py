"""
Tests the wrap_to_coroutine decorator.
"""
import asyncio

import pytest

from fsc.async_tools import wrap_to_coroutine


@wrap_to_coroutine
def wrap_func(*args, **kwargs):
    return args, kwargs


@wrap_to_coroutine
async def wrap_coro(*args, **kwargs):
    asyncio.sleep(0.)
    return args, kwargs


@pytest.mark.parametrize('coro', [wrap_func, wrap_coro])
@pytest.mark.parametrize('args', [(), (1, 2)])
@pytest.mark.parametrize('kwargs', [{}, {'a': 1}])
def test_wrap_to_coroutine(coro, args, kwargs):
    """
    Test wrapping different functions or coroutines to a coroutine.
    """
    fut = asyncio.ensure_future(coro(*args, **kwargs))
    asyncio.get_event_loop().run_until_complete(fut)
    assert fut.result() == (args, kwargs)
