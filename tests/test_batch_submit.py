"""
Defines tests for the BatchSubmitter.
"""

# pylint: disable=redefined-outer-name

import time
import asyncio

import pytest

from fsc.async_tools import BatchSubmitter


@pytest.fixture(params=[0., 1.])
def echo_submitter(request):
    echo = lambda x: x
    yield BatchSubmitter(echo, timeout=request.param)


@pytest.mark.parametrize('num_inputs', [10, 150, 300, 600])
def test_simple_submit(echo_submitter, num_inputs):
    """
    Tests with different number of inputs and timeout.
    """
    loop = asyncio.get_event_loop()
    input_ = list(range(num_inputs))
    fut = asyncio.gather(*[echo_submitter(i) for i in input_])
    loop.run_until_complete(fut)
    assert fut.result() == input_


def test_failing_run():
    """
    Test that errors in the function are correctly raised.
    """

    def func(x):  # pylint: disable=unused-argument
        raise ValueError

    loop = asyncio.get_event_loop()
    f = BatchSubmitter(func, timeout=0.)
    with pytest.raises(ValueError):
        loop.run_until_complete(f(1))


def test_start_twice(echo_submitter):
    """
    Test a BatchSubmitter where the submit loop needs to start twice.
    """
    loop = asyncio.get_event_loop()
    input_ = list(range(100))
    fut = asyncio.gather(*[echo_submitter(i) for i in input_])
    loop.run_until_complete(fut)
    assert fut.result() == input_
    time.sleep(1.)
    fut = asyncio.gather(*[echo_submitter(i) for i in input_])
    loop.run_until_complete(fut)
    assert fut.result() == input_


async def factorial(inp_list):  # pylint: disable=missing-docstring
    max_val = max(inp_list)
    assert max_val > 0
    results = [1]
    for val in range(1, max_val + 1):
        results.append(results[-1] * val)
    return [results[i] for i in inp_list]


def test_factorial():
    """
    Test BatchSubmitter with the factorial coroutine.
    """
    loop = asyncio.get_event_loop()
    func = BatchSubmitter(factorial, timeout=0., max_batch_size=1)
    res = loop.run_until_complete(asyncio.gather(func(4), func(3)))
    assert res == [24, 6]


async def recursive_coro_troll(inp_list):
    """
    A function that gives different results depending on the batch.
    """
    if all(inp <= 0 for inp in inp_list):
        return inp_list
    return await recursive_coro_troll([i - 1 for i in inp_list])


def test_recursive_calls():
    """
    Test BatchSubmitter with a recursive coroutine.
    """
    loop = asyncio.get_event_loop()
    func = BatchSubmitter(recursive_coro_troll, timeout=0., max_batch_size=1)
    res = loop.run_until_complete(asyncio.gather(func(3), func(6)))
    assert res == [0, 0]


def test_recursive_calls_timeout():
    """
    Test BatchSubmitter with a recursive coroutine, with different timings.
    """
    loop = asyncio.get_event_loop()
    func = BatchSubmitter(recursive_coro_troll, timeout=0.1, max_batch_size=2)
    res = loop.run_until_complete(asyncio.gather(func(3), func(6)))
    assert res == [-3, 0]
