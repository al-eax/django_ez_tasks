"""Tests for ThreadPoolBackend."""

import time
from django.test import TestCase
from django_ez_tasks.backends import ThreadPoolBackend
from tests.tasks import sleep_task
from .base import (
    BaseSignalTests,
    BaseSleepTaskTests,
    BaseContextTaskTests,
    BaseConcurrentTaskTests,
)


class TestThreadPoolBackendSleep(BaseSleepTaskTests, TestCase):
    """Sleep task tests for ThreadPoolBackend."""

    backend_class = ThreadPoolBackend
    backend_params = {"max_workers": 4}


class TestThreadPoolBackendContext(BaseContextTaskTests, TestCase):
    """Context task tests for ThreadPoolBackend."""

    backend_class = ThreadPoolBackend
    backend_params = {"max_workers": 4}


class TestThreadPoolBackendConcurrent(BaseConcurrentTaskTests, TestCase):
    """Concurrent task tests for ThreadPoolBackend."""

    backend_class = ThreadPoolBackend
    backend_params = {"max_workers": 4}


class TestThreadPoolBackendSignals(BaseSignalTests, TestCase):
    """Test signals for ThreadPoolBackend."""

    backend_class = ThreadPoolBackend
    backend_params = {"max_workers": 4}

    def test_multiple_tasks_signals(self):
        """Test signals for multiple concurrent tasks."""
        backend = self.get_backend("pool-multi-signal-test")

        # Enqueue 3 tasks
        results = []
        for _ in range(3):
            result = backend.enqueue(sleep_task, args=[], kwargs={"duration": 1})
            results.append(result)

        # All enqueued signals should be sent immediately
        self.assertEqual(len(self.enqueued_signals), 3)

        # Wait for all tasks to complete
        time.sleep(3)

        # All started and finished signals should be sent
        self.assertEqual(len(self.started_signals), 3)
        self.assertEqual(len(self.finished_signals), 3)

        # Verify all task ids are present
        enqueued_ids = {s["task_result"].id for s in self.enqueued_signals}
        started_ids = {s["task_result"].id for s in self.started_signals}
        finished_ids = {s["task_result"].id for s in self.finished_signals}
        result_ids = {r.id for r in results}

        self.assertEqual(enqueued_ids, result_ids)
        self.assertEqual(started_ids, result_ids)
        self.assertEqual(finished_ids, result_ids)
