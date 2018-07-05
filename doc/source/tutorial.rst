Tutorial
========

In this tutorial, the features of ``fsc.async-tools`` are briefly described.

PeriodicTask
------------

The :class:`.PeriodicTask` is an asynchronous contextmanager that can be used to regularly call a given function while the event loop is running.

As a simple example, consider the following function, which simply prints something to the terminal:

.. code:: python

    def snek():
        print('≻:======>···')


If we wish to run this function periodically, we can use the ``async with`` syntax:

.. include:: ../../examples/periodic_task.py
    :code: python

Additionally, you can control the delay between periodic tasks and whether the task is executed again when exiting the context manager, as described in the :class:`reference <.PeriodicTask>`.


wrap_to_coroutine
-----------------

The decorator :func:`.wrap_to_coroutine` simplifies creating interfaces which can take either a regular function or a coroutine. It wraps the input into a coroutine, which is compatible with the ``await`` syntax.

.. include:: ../../examples/wrap_to_coroutine.py
      :code: python

BatchSubmitter
--------------

The :class:`.BatchSubmitter` is useful when a function can run many inputs in parallel, but has a significant startup overhead. It can be called as a coroutine and will collect inputs, and then submit them as a batch to the wrapped function.

In the following example, the :class:`.BatchSubmitter` wraps a function which multiplies numbers by three. Due to the ``sleep`` call, each function evaluation takes at least a second, but it can then multiply many numbers quickly.

.. include:: ../../examples/batch_submit.py
    :code: python
