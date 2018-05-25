#!/usr/bin/env python
"""
Example for using the PeriodicTask to regularly call a function.
"""

import asyncio
from fsc.async_tools import PeriodicTask


def snek():
    print('≻:======>···')


async def run():
    print('start')
    async with PeriodicTask(snek):
        await asyncio.sleep(3)
    print('stop')


if __name__ == '__main__':
    LOOP = asyncio.get_event_loop()
    LOOP.run_until_complete(run())
