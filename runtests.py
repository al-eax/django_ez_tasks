#!/usr/bin/env python
"""
Run Django tests for django_ez_tasks.

Usage:
    python runtests.py
    python runtests.py tests.TestDjangoEzTask
    python runtests.py tests.TestDjangoEzTask.test_threaded_backend_sleep_task
"""
import sys

import django
from django.conf import settings
from django.test.utils import get_runner


def configure_settings():
    """Configure Django settings for testing."""
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": ":memory:",
                }
            },
            INSTALLED_APPS=[
                "django_ez_tasks",
            ],
        )


def run_tests(*test_labels):
    """Run the test suite."""
    configure_settings()
    django.setup()

    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2)

    if not test_labels:
        test_labels = ["tests"]

    failures = test_runner.run_tests(test_labels)
    sys.exit(bool(failures))


if __name__ == "__main__":
    run_tests(*sys.argv[1:])
