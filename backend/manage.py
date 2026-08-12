#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itams.settings')
    # manage.py is the developer entrypoint (runserver, test, shell, migrate), so it
    # opts into development mode. A deployment is served through itams/wsgi.py, which
    # does not pass through here and therefore gets the safe default: DEBUG off, and
    # no start-up at all without a real ITAMS_SECRET_KEY. Set ITAMS_DEBUG=0 to
    # exercise production settings locally.
    os.environ.setdefault('ITAMS_DEBUG', '1')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
