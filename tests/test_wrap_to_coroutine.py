"""
Tests the wrap_to_coroutine decorator.
"""
import asyncio
import inspect

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


def func_bare(x, y, *args, z, k=1, **kwargs):  # pylint: disable=unused-argument
    """test func docstring"""
    pass


async def coro_bare(x, y, *args, z, k=1, **kwargs):  # pylint: disable=unused-argument
    """test coro docstring"""
    pass


@pytest.mark.parametrize('func_to_wrap', [func_bare, coro_bare])
def test_doc_func(func_to_wrap):
    """
    Test that the docstring and signature of the wrapped function are preserved.
    """
    wrapped = wrap_to_coroutine(func_to_wrap)

    assert asyncio.iscoroutinefunction(wrapped)
    assert wrapped.__doc__ == func_to_wrap.__doc__
    assert wrapped.__name__ == func_to_wrap.__name__
    assert inspect.signature(func_to_wrap) == inspect.signature(wrapped)
    assert inspect.getfullargspec(func_to_wrap
                                  ) == inspect.getfullargspec(wrapped)
