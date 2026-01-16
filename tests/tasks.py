"""Task definitions for testing."""

import asyncio
import time
from django.tasks import task, TaskContext


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


@task(takes_context=True)
def context_task(context: TaskContext) -> dict:
    """A task that uses TaskContext and returns context information."""
    return {
        "task_id": context.task_result.id,
        "backend_name": context.task_result.backend,
    }


@task(takes_context=True)
def context_with_args_task(
    context: TaskContext, value: int, multiplier: int = 2
) -> dict:
    """A task that uses TaskContext along with additional arguments."""
    return {
        "task_id": context.task_result.id,
        "backend_name": context.task_result.backend,
        "result": value * multiplier,
    }


@task(takes_context=True)
async def async_context_task(context: TaskContext) -> dict:
    """An async task that uses TaskContext."""
    await asyncio.sleep(0.1)
    return {
        "task_id": context.task_result.id,
        "backend_name": context.task_result.backend,
    }


@task(takes_context=True)
async def async_context_with_args_task(
    context: TaskContext, value: int, multiplier: int = 2
) -> dict:
    """An async task that uses TaskContext along with additional arguments."""
    await asyncio.sleep(0.1)
    return {
        "task_id": context.task_result.id,
        "backend_name": context.task_result.backend,
        "result": value * multiplier,
    }
