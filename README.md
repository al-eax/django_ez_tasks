# Django EZ Tasks

A Django app built on top of [Django 6's Task framework](https://docs.djangoproject.com/en/6.0/topics/tasks/) that allows you to
run threaded tasks in background, without a database or worker process.


## Installation

```bash
 uv add git+https://github.com/al-eax/django_ez_tasks.git
```

## Quick Start

### 1. Add to INSTALLED_APPS

In your Django `settings.py`:

```python
INSTALLED_APPS = [
    # ... other apps
    "django_ez_tasks",
]
```

### 2. Configure Task Backends

Add your task configuration to `settings.py`:

```python
TASKS = {
    "default": {
        "BACKEND": "django_ez_tasks.backends.ThreadedBackend",
    }
}
```

Or use `ThreadPoolBackend` for a managed thread pool with configurable workers:

```python
TASKS = {
    "default": {
        "BACKEND": "django_ez_tasks.backends.ThreadPoolBackend",
        "OPTIONS": {
            "max_workers": 4,  # Number of threads in the pool
        }
    }
}
```

### 3. Usage

Define a task using the `@task` decorator:

```python
from django.tasks import task, default_task_backend
from django.tasks.signals import task_enqueued, task_started, task_finished

# Define tasks
@task
def send_welcome_email(user_id: int) -> str:
    """Send a welcome email to a new user."""
    user = User.objects.get(id=user_id)
    # Send email logic here...
    return f"Email sent to {user.email}"


# Connect signals (e.g., in your AppConfig.ready())
task_enqueued.connect(lambda sender, task_result, **kw: print(f"Task {task_result.id} enqueued"))
task_started.connect(lambda sender, task_result, **kw: print(f"Task {task_result.id} started"))
task_finished.connect(lambda sender, task_result, **kw: print(f"Task {task_result.id} finished: {task_result.status}, return value: {task_result.return_value}"))

# This returns immediately - the task runs in a background thread
result = send_welcome_email.enqueue(user_id=42)
task_id = result.id  # Save the task ID for later

# Retrieve the result later from anywhere in your code
task_result = default_task_backend.get_result(task_id)
print(task_result.status)        # e.g., TaskResultStatus.SUCCESSFUL
print(task_result.return_value)  # e.g., "Email sent to user@example.com"
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions, please visit the [GitHub repository](https://github.com/yourusername/django_ez_tasks).
