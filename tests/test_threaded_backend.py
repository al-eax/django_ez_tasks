"""Tests for ThreadedBackend."""

from django.test import TestCase
from django_ez_tasks.backends import ThreadedBackend
from .base import BaseSignalTests, BaseSleepTaskTests, BaseContextTaskTests


class TestThreadedBackendSleep(BaseSleepTaskTests, TestCase):
    """Sleep task tests for ThreadedBackend."""

    backend_class = ThreadedBackend
    backend_params = {}


class TestThreadedBackendContext(BaseContextTaskTests, TestCase):
    """Context task tests for ThreadedBackend."""

    backend_class = ThreadedBackend
    backend_params = {}


class TestThreadedBackendSignals(BaseSignalTests, TestCase):
    """Test signals for ThreadedBackend."""

    backend_class = ThreadedBackend
    backend_params = {}
