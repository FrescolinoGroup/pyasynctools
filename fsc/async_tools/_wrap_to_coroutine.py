"""
Defines a decorator for wrapping functions and coroutines into a coroutine.
"""

from functools import wraps
from collections.abc import Awaitable

from fsc.export import export


@export
def wrap_to_coroutine(func):
    """
    Wraps a function or coroutine into a coroutine.

    Arguments
    ---------
    func: Callable
        The function or coroutine that should be wrapped.
    """

    @wraps(func)
    async def inner(*args, **kwargs):  # pylint: disable=missing-docstring
        res = func(*args, **kwargs)
        if isinstance(res, Awaitable):
            return await res
        return res

    return inner
