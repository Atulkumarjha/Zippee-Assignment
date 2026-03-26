#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from dotenv import load_dotenv


def main():
    """Run administrative tasks."""
    load_dotenv()
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

    # Auto-migrate if running server
    if len(sys.argv) > 1 and sys.argv[1] == 'runserver':
        # Avoid running twice: run only in reloader process or if noreload is set
        if os.environ.get('RUN_MAIN') == 'true' or '--noreload' in sys.argv:
            try:
                import django
                django.setup()
                from django.core.management import call_command
                print("---------------------------------------------------------------------------")
                print("Auto-Running Migrations...")
                call_command('migrate', interactive=False)
                print("Migrations check completed.")
                print("---------------------------------------------------------------------------")
            except Exception as e:
                # If migration fails, log it but maybe catch specific errors if needed
                print(f"Warning: Auto-migration failed: {e}")

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
