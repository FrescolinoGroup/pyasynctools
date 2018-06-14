"""
Defines tests for the BatchSubmitter.
"""

# pylint: disable=redefined-outer-name

import asyncio

import pytest

from fsc.async_tools import BatchSubmitter


@pytest.fixture(params=[0., 1.])
def echo_submitter(request):
    echo = lambda x: x
    with BatchSubmitter(echo, timeout=request.param) as func:
        yield func


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
    with BatchSubmitter(func) as f:
        with pytest.raises(ValueError):
            loop.run_until_complete(f(1))


def test_manual_start_stop():
    """
    Test a BatchSubmitter that is manually started and stopped.
    """

    async def func(x):
        return x

    loop = asyncio.get_event_loop()
    submitter = BatchSubmitter(func)
    input_ = list(range(10))

    fut1 = asyncio.gather(*[submitter(i) for i in input_])
    submitter.start()
    loop.run_until_complete(fut1)
    assert fut1.result() == input_

    fut2 = asyncio.gather(*[submitter(i) for i in input_])
    submitter.stop()

    submitter.start()
    loop.run_until_complete(fut2)
    assert fut2.result() == input_
