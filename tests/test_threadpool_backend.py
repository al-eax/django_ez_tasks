"""Tests for ThreadPoolBackend."""

import time
from django.test import TestCase
from django_ez_tasks.backends import ThreadPoolBackend
from .tasks import sleep_task, async_sleep_task, async_compute_task


class TestThreadPoolBackend(TestCase):

    def test_threadpool_backend_sleep_task(self):
        """Test running a Django 6 task with ThreadPoolBackend."""
        backend = ThreadPoolBackend(alias="pool", params={"max_workers": 4})

        # Enqueue the task using the backend
        result = backend.enqueue(sleep_task, args=[], kwargs={"duration": 2})

        # Task is running in thread pool, so this returns immediately
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.id)

        # Wait for the task to complete
        time.sleep(3)

        # Check the result
        task_result = backend.get_result(result.id)
        self.assertIsNotNone(task_result)

    def test_threadpool_backend_concurrent_tasks(self):
        """Test running multiple concurrent tasks with ThreadPoolBackend."""
        backend = ThreadPoolBackend(alias="pool-concurrent", params={"max_workers": 4})

        start_time = time.time()

        # Enqueue 4 tasks that each sleep for 1 second
        results = []
        for i in range(4):
            result = backend.enqueue(sleep_task, args=[], kwargs={"duration": 1})
            results.append(result)

        # All 4 tasks should be enqueued
        self.assertEqual(len(results), 4)

        # Wait for all tasks to complete
        time.sleep(2)

        elapsed = time.time() - start_time

        # With 4 workers, 4 x 1-second tasks should complete in ~1 second (parallel)
        # not 4 seconds (sequential)
        self.assertLess(elapsed, 3)

        # Verify all results are retrievable
        for result in results:
            task_result = backend.get_result(result.id)
            self.assertIsNotNone(task_result)


class TestThreadPoolBackendAsync(TestCase):
    """Tests for async task execution with ThreadPoolBackend."""

    def test_threadpool_backend_async_task(self):
        """Test running an async Django 6 task with ThreadPoolBackend."""
        backend = ThreadPoolBackend(alias="async-pool", params={"max_workers": 4})

        # Enqueue the async task
        result = backend.enqueue(async_sleep_task, args=[], kwargs={"duration": 1})

        # Task is running in thread pool
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.id)

        # Wait for the task to complete
        time.sleep(2)

        # Check the result
        task_result = backend.get_result(result.id)
        self.assertIsNotNone(task_result)

    def test_threadpool_backend_concurrent_async_tasks(self):
        """Test running multiple concurrent async tasks with ThreadPoolBackend."""
        backend = ThreadPoolBackend(
            alias="async-pool-concurrent", params={"max_workers": 4}
        )

        start_time = time.time()

        # Enqueue 4 async tasks that each sleep for 1 second
        results = []
        for i in range(4):
            result = backend.enqueue(async_sleep_task, args=[], kwargs={"duration": 1})
            results.append(result)

        # All 4 tasks should be enqueued
        self.assertEqual(len(results), 4)

        # Wait for all tasks to complete
        time.sleep(3)

        elapsed = time.time() - start_time

        # With 4 workers, 4 x 1-second async tasks should complete in parallel
        self.assertLess(elapsed, 4)

        # Verify all results are retrievable
        for result in results:
            task_result = backend.get_result(result.id)
            self.assertIsNotNone(task_result)

    def test_async_compute_task(self):
        """Test running an async compute task."""
        backend = ThreadPoolBackend(alias="async-compute", params={"max_workers": 2})

        # Enqueue the async compute task
        result = backend.enqueue(async_compute_task, args=[], kwargs={"n": 100})

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.id)

        # Wait for the task to complete
        time.sleep(2)

        # Check the result
        task_result = backend.get_result(result.id)
        self.assertIsNotNone(task_result)
