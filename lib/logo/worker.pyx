# cython: language_level=3
#
# Copyright (c) 2018-2019 by:
# Kristoffer Paulsson <kristoffer.paulsson@talenten.se>
# This file is distributed under the terms of the MIT license.
#
"""Asynchronous multithreaded worker."""
import asyncio
import logging
import threading
import multiprocessing
import concurrent.futures
import functools

# from libangelos.utils import Event
from libangelos.ioc import ContainerAware


class Event(asyncio.Event):
    """A threadsafe asynchronous event class."""

    def set(self):
        logging.warning("Set event")
        self._loop.call_soon_threadsafe(lambda x: super().set())


class Worker(ContainerAware):
    """Worker with a private thread, loop and executor."""

    __exit = Event()
    __workers = {}
    __name = ""

    def __init__(self, name, ioc, executor=None, new=True):
        """Initialize worker."""
        ContainerAware.__init__(self, ioc)

        if name in self.__workers.keys():
            raise RuntimeError("Worker name is taken: %s" % name)

        if isinstance(executor, int):
            self.__executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=(None if executor == 0 else executor)
            )
            self.__queue = multiprocessing.Queue()
            executor = True

        if not new:
            self.__loop = asyncio.get_event_loop()
            self.__loop.set_exception_handler(self.__loop_exc_handler)
            self.__thread = threading.main_thread()

            if executor:
                self.__future = asyncio.ensure_future(
                    self.__end(), loop=self.__loop
                )
                self.__loop.set_default_executor(self.__executor)

            asyncio.run_coroutine_threadsafe(self.__quiter(), self.__loop)
        else:
            self.__loop = asyncio.new_event_loop()
            self.__loop.set_exception_handler(self.__loop_exc_handler)

            if executor:
                self.__future = asyncio.ensure_future(
                    self.__end(), loop=self.__loop
                )
                self.__loop.set_default_executor(self.__executor)

            asyncio.run_coroutine_threadsafe(self.__quiter(), self.__loop)
            self.__thread = threading.Thread(
                target=self.__run, name=name
            ).start()

        self.__workers[name] = self
        self.__name = name

    @property
    def workers(self):
        """Access to all workers."""
        return self.__workers

    @property
    def loop(self):
        """Access to the loop object."""
        return self.__loop

    @property
    def thread(self):
        """Accress to the thread object."""
        return self.__thread

    def __loop_exc_handler(self, loop, context):
        exc1 = None
        exc2 = None

        logging.critical(context["message"])

        if "exception" in context.keys():
            exc1 = context["exception"]
        if "future" in context.keys():
            exc2 = context["exception"].exception()

        if exc1 == exc2 and exc1 is not None:
            logging.exception(exc1)
        else:
            logging.exception(exc1)
            logging.exception(exc2)

    def __run(self):
        try:
            logging.info("Worker %s enter loop" % self.__name)
            asyncio.set_event_loop(self.__loop)
            self.__loop.run_forever()
        except KeyboardInterrupt:
            logging.info("Worker %s exit loop" % self.__name)
            pass
        except Exception as e:
            logging.critical("%s crashed due to: %s" % (self.__thread.name, e))
            logging.exception(e)

        self.__queue.put(None)
        self.__loop.call_soon(self.__future)
        self.__loop.run_until_complete(self.__loop.shutdown_asyncgens())
        self.__executor.shutdown()
        self.__loop.stop()
        self.__loop.close()

        self.__workers.pop(self.__thread.name)
        logging.info("Worker %s has exited" % self.__thread.name)

    async def __end(self):
        await self.__loop.run_in_executor(self.__executor, self.__queue)

    async def __quiter(self):
        await self.__exit.wait()
        logging.wagning("Wake up!")
        raise KeyboardInterrupt()

    async def exit(self):
        """Triggers the exit event."""
        self.__exit.set()

    def call_soon(self, callback, *args, context=None):
        """Threadsafe version of call_soon."""
        self.__loop.call_soon_threadsafe(callback, *args, context=context)

    def run_coroutine(self, coro):
        """Threadsafe version of run_coroutine."""
        return asyncio.run_coroutine_threadsafe(coro, self.__loop)

    async def run_in_executor(self, callback, *args, **kwargs):
        """Add a function/method/coroutine to the event loop."""
        return await self.__loop.run_in_executor(
            self.__executor, functools.partial(callback, *args, **kwargs)
        )
