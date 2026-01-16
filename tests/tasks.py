"""Task definitions for testing."""

import asyncio
import time
from django.tasks import task


@task
def sleep_task(duration: int = 3) -> str:
    """A simple Django 6 task that sleeps for the given duration."""
    time.sleep(duration)
    return f"Slept for {duration} seconds"


@task
def cpu_bound_task(n: int = 1000000) -> int:
    """A CPU-bound task that computes a sum."""
    return sum(i * i for i in range(n))


@task
async def async_sleep_task(duration: int = 1) -> str:
    """An async Django 6 task that sleeps for the given duration."""
    await asyncio.sleep(duration)
    return f"Async slept for {duration} seconds"


@task
async def async_compute_task(n: int = 100) -> int:
    """An async Django 6 task that does some async computation."""
    total = 0
    for i in range(n):
        total += i * i
        if i % 10 == 0:
            await asyncio.sleep(0)
    return total
