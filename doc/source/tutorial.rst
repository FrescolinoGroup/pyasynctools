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
