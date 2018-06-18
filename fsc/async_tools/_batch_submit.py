"""
Defines a context manager that can be used to group calls to a 'listable'
function into batches.
"""

import asyncio

from fsc.export import export

from . import wrap_to_coroutine


@export
class BatchSubmitter:
    """
    Context manager that collects calls to a function of one parameter, and submits
    it in batches to a function which can take a list of parameters.

    Arguments
    ---------
    func: Callable
        Function or coroutine which is "listable", i.e. given a list of input
        parameters it will return a list of results.
    loop: EventLoop
        The event loop on which the batch submitter runs. Uses
        ``asyncio.get_event_loop()`` by default.
    timeout: float
        Maximum time after which the batch submitter will submit all current
        tasks, even if the minimum batch size is not reached.
    sleep_time : float
        Time the batch submitter will sleep between checking if the minimum
        batch size has been reached, and checking if there are finished
        calculations.
    min_batch_size : int
        Minimum batch size that will be submitted before the timeout has been
        reached.
    max_batch_size : int
        The maximum size of a batch that will be submitted.
    """

    def __init__(
        self,
        func,
        *,
        loop=None,
        timeout=0.,
        sleep_time=0.1,
        min_batch_size=100,
        max_batch_size=1000
    ):
        self._func = wrap_to_coroutine(func)
        self._loop = loop or asyncio.get_event_loop()
        self._timeout = timeout
        self._sleep_time = sleep_time
        self._min_batch_size = min_batch_size
        self._max_batch_size = max_batch_size
        self._tasks = asyncio.Queue()
        self._batches = dict()
        self._submit_loop_running = False
        self._last_call_time = None

    async def __call__(self, x):
        """
        Adds a task for the given input, and starts the submission loop if needed.
        """
        fut = self._loop.create_future()
        self._tasks.put_nowait((x, fut))
        self._last_call_time = self._loop.time()
        if not self._submit_loop_running:
            asyncio.Task(self._submit_loop(), loop=self._loop)
            self._submit_loop_running = True
        return await fut

    async def _submit_loop(self):
        """
        Waits for tasks and then creates the batches which evaluate the function.
        """
        while self._tasks:
            await self._wait_for_tasks()
            self._launch_batch()
        self._submit_loop_running = False

    async def _wait_for_tasks(self):
        """
        Waits until either the timeout has passed or the queue size is big enough.
        """
        assert self._tasks.qsize() > 0
        while self._loop.time() - self._last_call_time < self._timeout:
            if self._tasks.qsize() >= self._min_batch_size:
                return
            await asyncio.sleep(self._sleep_time)

    def _launch_batch(self):
        """
        Launch a calculation batch.
        """
        inputs = []
        futures = []
        for _ in range(self._max_batch_size):
            try:
                key, fut = self._tasks.get_nowait()
                inputs.append(key)
                futures.append(fut)
            except asyncio.QueueEmpty:
                break
        task = asyncio.ensure_future(self._func(inputs))
        task.add_done_callback(self._process_finished_batch)
        self._batches[task] = futures

    def _process_finished_batch(self, batch_future):
        """
        Assign the results / exceptions to the futures of all finished batches.
        """
        try:
            task_futures = self._batches[batch_future]
            results = batch_future.result()
            assert len(results) == len(task_futures)
            for fut, res in zip(task_futures, results):
                fut.set_result(res)
        except Exception as exc:  # pylint: disable=broad-except
            for fut in task_futures:
                fut.set_exception(exc)
        finally:
            del self._batches[batch_future]
