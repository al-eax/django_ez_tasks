"""Base test classes and utilities for backend tests."""

import time
from django.tasks import TaskResultStatus
from django.tasks.signals import task_enqueued, task_started, task_finished

from .tasks import sleep_task


# pylint: disable=no-member


class BackendTestMixin:
    """Mixin providing common test methods for task backends."""

    backend_class = None
    backend_params = {}

    def get_backend(self, alias="default"):
        """Create a backend instance with the given alias."""
        return self.backend_class(alias=alias, params=self.backend_params)

    def wait_for_result(self, backend, result, timeout=2):
        """Wait for a task to complete and return the result."""
        time.sleep(timeout)
        return backend.get_result(result.id)

    def assertTaskSuccessful(
        self, task_result, msg=None
    ):  # pylint: disable=invalid-name
        """Assert that a task completed successfully."""
        self.assertEqual(
            task_result.status,
            TaskResultStatus.SUCCESSFUL,
            msg or f"Task failed with errors: {task_result.errors}",
        )


class BaseSleepTaskTests(BackendTestMixin):
    """Base tests for sleep tasks - subclass and set backend_class."""

    def test_sleep_task(self):
        """Test running a Django 6 task with the backend."""
        from .tasks import sleep_task

        backend = self.get_backend("sleep-test")
        result = backend.enqueue(sleep_task, args=[], kwargs={"duration": 1})

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.id)

        task_result = self.wait_for_result(backend, result, timeout=2)
        self.assertIsNotNone(task_result)
        self.assertEqual(task_result.return_value, "Slept for 1 seconds")

    def test_async_sleep_task(self):
        """Test running an async Django 6 task with the backend."""
        from .tasks import async_sleep_task

        backend = self.get_backend("async-sleep-test")
        result = backend.enqueue(async_sleep_task, args=[], kwargs={"duration": 1})

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.id)

        task_result = self.wait_for_result(backend, result, timeout=2)
        self.assertIsNotNone(task_result)
        self.assertEqual(task_result.return_value, "Async slept for 1 seconds")


class BaseContextTaskTests(BackendTestMixin):
    """Base tests for tasks with TaskContext - subclass and set backend_class."""

    def test_context_task(self):
        """Test running a task with TaskContext."""
        from .tasks import context_task

        backend = self.get_backend("context-test")
        result = backend.enqueue(context_task, args=[], kwargs={})

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.id)

        task_result = self.wait_for_result(backend, result, timeout=1)
        self.assertIsNotNone(task_result)
        self.assertTaskSuccessful(task_result)

        return_value = task_result.return_value
        self.assertEqual(return_value["task_id"], result.id)
        self.assertEqual(return_value["backend_name"], "context-test")

    def test_context_with_args_task(self):
        """Test running a task with TaskContext and additional arguments."""
        from .tasks import context_with_args_task

        backend = self.get_backend("context-args-test")
        result = backend.enqueue(
            context_with_args_task, args=[], kwargs={"value": 5, "multiplier": 3}
        )

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.id)

        task_result = self.wait_for_result(backend, result, timeout=1)
        self.assertIsNotNone(task_result)
        self.assertTaskSuccessful(task_result)

        return_value = task_result.return_value
        self.assertEqual(return_value["task_id"], result.id)
        self.assertEqual(return_value["backend_name"], "context-args-test")
        self.assertEqual(return_value["result"], 15)  # 5 * 3

    def test_context_with_positional_args(self):
        """Test running a task with TaskContext using positional arguments."""
        from .tasks import context_with_args_task

        backend = self.get_backend("context-pos-test")
        result = backend.enqueue(
            context_with_args_task, args=[10], kwargs={"multiplier": 4}
        )

        self.assertIsNotNone(result)

        task_result = self.wait_for_result(backend, result, timeout=1)
        self.assertTaskSuccessful(task_result)
        self.assertEqual(task_result.return_value["result"], 40)  # 10 * 4

    def test_async_context_task(self):
        """Test running an async task with TaskContext."""
        from .tasks import async_context_task

        backend = self.get_backend("async-context-test")
        result = backend.enqueue(async_context_task, args=[], kwargs={})

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.id)

        task_result = self.wait_for_result(backend, result, timeout=1)
        self.assertIsNotNone(task_result)
        self.assertTaskSuccessful(task_result)

        return_value = task_result.return_value
        self.assertEqual(return_value["task_id"], result.id)
        self.assertEqual(return_value["backend_name"], "async-context-test")

    def test_async_context_with_args_task(self):
        """Test running an async task with TaskContext and arguments."""
        from .tasks import async_context_with_args_task

        backend = self.get_backend("async-context-args-test")
        result = backend.enqueue(
            async_context_with_args_task, args=[], kwargs={"value": 7, "multiplier": 6}
        )

        self.assertIsNotNone(result)

        task_result = self.wait_for_result(backend, result, timeout=1)
        self.assertTaskSuccessful(task_result)

        return_value = task_result.return_value
        self.assertEqual(return_value["task_id"], result.id)
        self.assertEqual(return_value["backend_name"], "async-context-args-test")
        self.assertEqual(return_value["result"], 42)  # 7 * 6


class BaseConcurrentTaskTests(BackendTestMixin):
    """Base tests for concurrent task execution - subclass and set backend_class."""

    def test_concurrent_tasks(self):
        """Test running multiple concurrent tasks."""
        from .tasks import sleep_task

        backend = self.get_backend("concurrent-test")
        start_time = time.time()

        # Enqueue 4 tasks that each sleep for 1 second
        results = []
        for _ in range(4):
            result = backend.enqueue(sleep_task, args=[], kwargs={"duration": 1})
            results.append(result)

        self.assertEqual(len(results), 4)

        # Wait for all tasks to complete
        time.sleep(2)
        elapsed = time.time() - start_time

        # With parallel execution, should complete in ~1-2 seconds, not 4
        self.assertLess(elapsed, 3)

        # Verify all results are retrievable
        for result in results:
            task_result = backend.get_result(result.id)
            self.assertIsNotNone(task_result)

    def test_concurrent_context_tasks(self):
        """Test running multiple concurrent tasks with TaskContext."""
        from .tasks import context_with_args_task

        backend = self.get_backend("concurrent-ctx-test")

        results = []
        for i in range(4):
            result = backend.enqueue(
                context_with_args_task, args=[], kwargs={"value": i, "multiplier": 2}
            )
            results.append(result)

        self.assertEqual(len(results), 4)

        # Wait for all tasks to complete
        time.sleep(2)

        # Verify all results
        for i, result in enumerate(results):
            task_result = backend.get_result(result.id)
            self.assertTaskSuccessful(task_result)
            self.assertEqual(task_result.return_value["task_id"], result.id)
            self.assertEqual(task_result.return_value["result"], i * 2)


class SignalTestMixin(BackendTestMixin):
    """Mixin for testing task signals."""

    backend_class = None
    backend_params = {}

    def setUp(self):
        """Set up signal tracking."""
        self.enqueued_signals = []
        self.started_signals = []
        self.finished_signals = []

        # Connect signal handlers
        task_enqueued.connect(self.on_task_enqueued)
        task_started.connect(self.on_task_started)
        task_finished.connect(self.on_task_finished)

    def tearDown(self):
        """Disconnect signal handlers."""
        task_enqueued.disconnect(self.on_task_enqueued)
        task_started.disconnect(self.on_task_started)
        task_finished.disconnect(self.on_task_finished)

    def on_task_enqueued(self, sender, task_result, **kwargs):
        """Record enqueued signal."""
        self.enqueued_signals.append(
            {
                "sender": sender,
                "task_result": task_result,
            }
        )

    def on_task_started(self, sender, task_result, **kwargs):
        """Record started signal."""
        self.started_signals.append(
            {
                "sender": sender,
                "task_result": task_result,
            }
        )

    def on_task_finished(self, sender, task_result, **kwargs):
        """Record finished signal."""
        self.finished_signals.append(
            {
                "sender": sender,
                "task_result": task_result,
            }
        )


class BaseSignalTests(SignalTestMixin):
    """Base tests for task signals.

    Must be combined with TestCase in subclass:
        class MyTest(BaseSignalTests, TestCase):
            backend_class = MyBackend
    """

    def test_task_enqueued_signal(self):
        """Test that task_enqueued signal is sent when task is enqueued."""
        backend = self.get_backend("signal-enqueue-test")
        result = backend.enqueue(sleep_task, args=[], kwargs={"duration": 1})

        # Signal should be sent immediately on enqueue
        self.assertEqual(len(self.enqueued_signals), 1)
        self.assertEqual(self.enqueued_signals[0]["task_result"].id, result.id)

        # Wait for task to complete
        time.sleep(2)

    def test_task_started_signal(self):
        """Test that task_started signal is sent when task starts executing."""
        backend = self.get_backend("signal-started-test")
        backend.enqueue(sleep_task, args=[], kwargs={"duration": 1})

        # Wait for task to start and finish
        time.sleep(2)

        # Started signal should have been sent
        self.assertEqual(len(self.started_signals), 1)

    def test_task_finished_signal(self):
        """Test that task_finished signal is sent when task completes."""
        backend = self.get_backend("signal-finished-test")
        result = backend.enqueue(sleep_task, args=[], kwargs={"duration": 1})

        # Wait for task to complete
        time.sleep(2)

        # Finished signal should have been sent
        self.assertEqual(len(self.finished_signals), 1)
        self.assertEqual(self.finished_signals[0]["task_result"].id, result.id)

    def test_all_signals_sent_in_order(self):
        """Test that all signals are sent in correct order."""
        backend = self.get_backend("signal-order-test")
        result = backend.enqueue(sleep_task, args=[], kwargs={"duration": 1})

        # Wait for task to complete
        time.sleep(2)

        # All signals should be sent
        self.assertEqual(len(self.enqueued_signals), 1)
        self.assertEqual(len(self.started_signals), 1)
        self.assertEqual(len(self.finished_signals), 1)

        # Verify task_result ids match
        self.assertEqual(self.enqueued_signals[0]["task_result"].id, result.id)
        self.assertEqual(self.started_signals[0]["task_result"].id, result.id)
        self.assertEqual(self.finished_signals[0]["task_result"].id, result.id)

    def test_finished_signal_contains_successful_status(self):
        """Test that finished signal contains successful status."""
        backend = self.get_backend("signal-status-test")
        backend.enqueue(sleep_task, args=[], kwargs={"duration": 1})

        # Wait for task to complete
        time.sleep(2)

        # Check status in finished signal
        self.assertEqual(len(self.finished_signals), 1)
        self.assertEqual(
            self.finished_signals[0]["task_result"].status,
            TaskResultStatus.SUCCESSFUL,
        )
