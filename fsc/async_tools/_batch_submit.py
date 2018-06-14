"""
Defines a context manager that can be used to group calls to a 'listable'
function into batches.
"""

import time
import asyncio

from . import wrap_to_coroutine


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
        self._run_task = None
        self._batches = dict()
        self._create_task = None
        self._collect_task = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self):
        """
        Starts the BatchSubmitter. Tasks will only be executed once the event loop is started.
        """
        self._create_task = asyncio.Task(self._create(), loop=self._loop)
        self._collect_task = asyncio.Task(self._collect(), loop=self._loop)

    def stop(self):
        """
        Stops the BatchSubmitter. Pending tasks be evaluated once the BatchSubmitter is started again.
        """
        self._create_task.cancel()
        self._collect_task.cancel()
        self._process_finished_batches()
        self._create_task = None
        self._collect_task = None

    async def _create(self):
        """
        Waits for tasks and then creates the batches which evaluate the function.
        """
        while True:
            await self._wait_for_tasks()
            self._launch_batch()

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
        self._batches[asyncio.ensure_future(self._func(inputs))] = futures

    async def _wait_for_tasks(self):
        """
        Waits until either the timeout has passed or the queue size is big enough.
        """
        while True:
            start_time = time.time()
            while time.time() - start_time < self._timeout:
                if self._tasks.qsize() >= self._min_batch_size:
                    return
                await asyncio.sleep(self._sleep_time)
            if self._tasks.qsize() > 0:
                return
            await asyncio.sleep(0)

    async def _collect(self):
        """
        Evaluates finished batches.
        """
        while True:
            await asyncio.sleep(self._sleep_time)
            self._process_finished_batches()

    def _process_finished_batches(self):
        """
        Assign the results / exceptions to the futures of all finished batches.
        """
        for batch_future, task_futures in list(self._batches.items()):
            if batch_future.done():
                try:
                    results = batch_future.result()
                    assert len(results) == len(task_futures)
                    for fut, res in zip(task_futures, results):
                        fut.set_result(res)
                except Exception as exc:  # pylint: disable=broad-except
                    for fut in task_futures:
                        fut.set_exception(exc)
                finally:
                    del self._batches[batch_future]

    async def __call__(self, x):
        fut = self._loop.create_future()
        self._tasks.put_nowait((x, fut))
        return await fut
