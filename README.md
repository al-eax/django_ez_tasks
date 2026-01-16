# Django EZ Tasks

A simple,  Django app for managing background tasks with multiple execution backends. 
Built on Django 6's BackgroundTask API with additional simple backends.


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
from django.tasks import task

@task
def send_welcome_email(user_id: int) -> str:
    """Send a welcome email to a new user."""
    user = User.objects.get(id=user_id)
    # Send email logic here...
    return f"Email sent to {user.email}"


# This returns immediately - the task runs in a background thread
result = send_welcome_email.enqueue(user_id=42)

# You can check the result later
print(result.id)  # Task ID for tracking
```


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions, please visit the [GitHub repository](https://github.com/yourusername/django_ez_tasks).
