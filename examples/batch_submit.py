#!/usr/bin/env python
"""
Example for using the BatchSubmitter to collect calls to a function.
"""

import time
import asyncio

import numpy as np
from fsc.async_tools import BatchSubmitter


def function(x):
    time.sleep(1.)
    return np.array(x) * 3


def main():
    """
    Run the 'BatchSubmitter' example.
    """
    loop = asyncio.get_event_loop()
    inputs = range(100)
    results_direct = np.array(inputs) * 3
    func = BatchSubmitter(function)
    start = time.time()
    results = loop.run_until_complete(
        asyncio.gather(*[func(i) for i in inputs])
    )
    results = loop.run_until_complete(
        asyncio.gather(*[func(i) for i in inputs])
    )
    end = time.time()
    assert np.all(results == results_direct)

    print('Batch submit ran in {:.2f} seconds.'.format(end - start))


if __name__ == '__main__':
    main()
