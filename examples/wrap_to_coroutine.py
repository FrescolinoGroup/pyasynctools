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
    asyncio.sleep(0.)
    return '≻:======>···'


if __name__ == '__main__':
    LOOP = asyncio.get_event_loop()
    FUT_SYNC = asyncio.ensure_future(sync_snek())
    FUT_ASYNC = asyncio.ensure_future(async_snek())
    LOOP.run_until_complete(asyncio.gather(FUT_SYNC, FUT_ASYNC))

    print('sync snek ', FUT_SYNC.result())
    print('async snek', FUT_ASYNC.result())
