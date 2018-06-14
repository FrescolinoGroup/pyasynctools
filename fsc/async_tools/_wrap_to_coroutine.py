"""
Defines a decorator for wrapping functions and coroutines into a coroutine.
"""

from collections.abc import Awaitable

from decorator import decorator

from fsc.export import export


@export
@decorator
async def wrap_to_coroutine(func, *args, **kwargs):
    """
    Wraps a function or coroutine into a coroutine.

    Arguments
    ---------
    func: Callable
        The function or coroutine that should be wrapped.
    """

    res = func(*args, **kwargs)
    if isinstance(res, Awaitable):
        return await res
    return res
