import time
from django.test import TestCase
from django_ez_tasks.backends import ThreadedBackend
from .tasks import sleep_task, async_sleep_task


class TestThreadedBackend(TestCase):

    def test_threaded_backend_sleep_task(self):
        """Test running a Django 6 task with ThreadedBackend."""
        backend = ThreadedBackend(alias="default", params={})

        # Enqueue the task using the backend
        result = backend.enqueue(sleep_task, args=[], kwargs={"duration": 3})

        # Task is running in a separate thread, so this returns immediately
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.id)

        # Wait for the task to complete
        time.sleep(4)

        # Check the result
        task_result = backend.get_result(result.id)
        self.assertIsNotNone(task_result)
        self.assertEqual(task_result, "Slept for 3 seconds")

    def test_threaded_backend_async_task(self):
        """Test running an async Django 6 task with ThreadedBackend."""
        backend = ThreadedBackend(alias="async-threaded", params={})

        # Enqueue the async task
        result = backend.enqueue(async_sleep_task, args=[], kwargs={"duration": 1})

        # Task is running in a separate thread
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.id)

        # Wait for the task to complete
        time.sleep(2)

        # Check the result
        task_result = backend.get_result(result.id)
        self.assertIsNotNone(task_result)
        self.assertEqual(task_result, "Async slept for 1 seconds")
