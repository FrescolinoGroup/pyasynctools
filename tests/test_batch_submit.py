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
    f = BatchSubmitter(func)
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
