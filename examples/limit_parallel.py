#!/usr/bin/env python
"""
Example for using the limit_parallel decorator.
"""

import asyncio

import numpy as np
from fsc.async_tools import limit_parallel


async def use_some_memory():
    """
    Dummy function which initializes a large array.
    """
    x = np.ones(shape=(10000000, ))
    await asyncio.sleep(3.)
    del x


def launch_many(coro_func):
    """
    Launch the given coroutine function one hundred times.
    """
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(
        asyncio.
        gather(*[asyncio.ensure_future(coro_func()) for _ in range(100)])
    )


if __name__ == '__main__':
    print('Without limiter...')
    launch_many(use_some_memory)
    print('With limiter...')
    launch_many(limit_parallel(10)(use_some_memory))
