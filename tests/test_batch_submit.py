"""
Defines tests for the BatchSubmitter.
"""

# pylint: disable=redefined-outer-name

import asyncio

import pytest

from fsc.async_tools import BatchSubmitter, PeriodicTask


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


def test_start_stop():
    """
    Test a BatchSubmitter that is manually started and stopped.
    """

    async def func(x):
        await asyncio.sleep(0.1)
        return x

    async def run():  # pylint: disable=missing-docstring
        submitter = BatchSubmitter(
            func,
            min_batch_size=3,
            max_batch_size=5,
            sleep_time=0.,
            timeout=0.2
        )
        count = 0

        def stopstart():
            nonlocal count
            count += 1
            submitter.stop()
            submitter.start()

        inputs = list(range(50))
        futures = []
        submitter.start()
        async with PeriodicTask(stopstart, delay=0.1):
            for i in inputs:
                await asyncio.sleep(0.01)
                futures.append(asyncio.ensure_future(submitter(i)))

        results = await asyncio.gather(*futures)
        assert count > 4
        assert inputs == results

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
