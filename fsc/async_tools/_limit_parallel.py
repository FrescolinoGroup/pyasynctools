"""
Defines a decorator that limits the number of parallel calls to a function
or coroutine.
"""

import asyncio
from functools import wraps

from fsc.export import export

from . import wrap_to_coroutine


@export
def limit_parallel(max_num_parallel):
    """
    Decorator that limits the number of parallel calls to a function or coroutine.

    Arguments
    ---------
    max_num_parallel : int
        The maximum number of calls which can run in parallel.
    """

    def decorator(func):  # pylint: disable=missing-docstring
        semaphore = asyncio.Semaphore(value=max_num_parallel)
        func_wrapped = wrap_to_coroutine(func)

        @wraps(func)
        async def inner(*args, **kwargs):  # pylint: disable=missing-docstring
            nonlocal semaphore
            await semaphore.acquire()
            try:
                res = await func_wrapped(*args, **kwargs)
            finally:
                semaphore.release()
            return res

        return inner

    return decorator
