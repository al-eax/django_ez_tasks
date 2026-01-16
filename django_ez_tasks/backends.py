"""Custom Django task backend that executes tasks in separate threads."""

import logging
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from multiprocessing import Manager

from django.tasks.backends.immediate import ImmediateBackend
from django.utils.crypto import get_random_string
from django.tasks import TaskResult, TaskResultStatus

logger = logging.getLogger(__name__)


class ThreadedBackend(ImmediateBackend):
    """
    A task backend that executes tasks in separate threads (non-blocking).

    """

    # In-memory store for task results
    _results = {}
    _lock = threading.Lock()
    supports_get_result = True

    def enqueue(self, task, args, kwargs):
        """
        Enqueue a task to run in a separate thread.

        Args:
            task: The task function to execute
            args: Positional arguments for the task
            kwargs: Keyword arguments for the task

        Returns:
            TaskResult: The task result object
        """
        self.validate_task(task)

        # Create the task result (from parent class logic)

        task_result = TaskResult(
            task=task,
            id=get_random_string(32),
            status=TaskResultStatus.READY,
            enqueued_at=None,
            started_at=None,
            last_attempted_at=None,
            finished_at=None,
            args=args,
            kwargs=kwargs,
            backend=self.alias,
            errors=[],
            worker_ids=[],
        )

        # Keep result available for retrieval
        with self._lock:
            self._results[task_result.id] = task_result

        # Execute in a separate thread
        thread = threading.Thread(
            target=self._execute_task,
            args=(task_result,),
            daemon=True,
            name=f"task-{task_result.id}",
        )
        thread.start()

        return task_result

    def get_result(self, result_id):
        """Return a previously enqueued TaskResult from memory."""
        with self._lock:
            return self._results[result_id]


class ThreadPoolBackend(ImmediateBackend):
    """
    A task backend that executes tasks using a ThreadPoolExecutor.

    Configuration options (via TASKS settings):
        max_workers: Maximum number of threads in the pool (default: 4)
    """

    # Shared results store across all instances
    _results = {}
    _lock = threading.Lock()
    _executors = {}  # Per-alias executor instances
    supports_get_result = True

    def __init__(self, alias, params):
        super().__init__(alias, params)
        self.max_workers = params.get("max_workers", 4)

        # Create executor for this alias if it doesn't exist
        with self._lock:
            if alias not in self._executors:
                self._executors[alias] = ThreadPoolExecutor(
                    max_workers=self.max_workers,
                    thread_name_prefix=f"task-pool-{alias}",
                )
            self._executor = self._executors[alias]

    def enqueue(self, task, args, kwargs):
        """
        Enqueue a task to run in the thread pool.

        Args:
            task: The task function to execute
            args: Positional arguments for the task
            kwargs: Keyword arguments for the task

        Returns:
            TaskResult: The task result object
        """
        self.validate_task(task)

        task_result = TaskResult(
            task=task,
            id=get_random_string(32),
            status=TaskResultStatus.READY,
            enqueued_at=None,
            started_at=None,
            last_attempted_at=None,
            finished_at=None,
            args=args,
            kwargs=kwargs,
            backend=self.alias,
            errors=[],
            worker_ids=[],
        )

        # Store result for later retrieval
        with self._lock:
            self._results[task_result.id] = task_result

        # Submit to thread pool
        self._executor.submit(self._execute_task, task_result)

        return task_result

    def get_result(self, result_id):
        """Return a previously enqueued TaskResult from memory."""
        with self._lock:
            return self._results[result_id]

    @classmethod
    def shutdown_all(cls, wait=True):
        """Shutdown all thread pool executors."""
        with cls._lock:
            for executor in cls._executors.values():
                executor.shutdown(wait=wait)
            cls._executors.clear()
