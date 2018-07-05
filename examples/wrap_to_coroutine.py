#!/usr/bin/env python
"""
Example of wrapping a function and a coroutine into a coroutine using 'wrap_to_coroutine'.
"""

import asyncio

from fsc.async_tools import wrap_to_coroutine


@wrap_to_coroutine
def sync_snek():
    return '≻:======>···'


@wrap_to_coroutine
async def async_snek():
    await asyncio.sleep(0.)
    return '≻:======>···'


def main():
    """
    Run the 'wrap_to_coroutine' example.
    """
    loop = asyncio.get_event_loop()
    fut_sync = asyncio.ensure_future(sync_snek())
    fut_async = asyncio.ensure_future(async_snek())
    loop.run_until_complete(asyncio.gather(fut_sync, fut_async))

    print('sync snek ', fut_sync.result())
    print('async snek', fut_async.result())


if __name__ == '__main__':
    main()
