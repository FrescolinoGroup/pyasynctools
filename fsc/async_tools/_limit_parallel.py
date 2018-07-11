"""
Defines a decorator that limits the number of parallel calls to a function
or coroutine.
"""

import asyncio
from functools import wraps

from fsc.export import export

from . import wrap_to_coroutine


@export
def limit_parallel(max_num_parallel, sleep_time=0.):
    """
    Decorator that limits the number of parallel calls to a function or coroutine.

    Arguments
    ---------
    max_num_parallel : int
        The maximum number of calls which can run in parallel.
    sleep_time : float, optional
        Minimum wait time between checking if the function can be called.
    """

    def decorator(func):  # pylint: disable=missing-docstring
        count = 0

        func_wrapped = wrap_to_coroutine(func)

        @wraps(func)
        async def inner(*args, **kwargs):  # pylint: disable=missing-docstring
            nonlocal count
            while count >= max_num_parallel:
                await asyncio.sleep(sleep_time)
            count += 1
            try:
                res = await func_wrapped(*args, **kwargs)
            finally:
                count -= 1
            return res

        return inner

    return decorator
