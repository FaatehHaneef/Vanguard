#!/usr/bin/env python
"""Django's command-line utility for Pantry Notes."""

import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pantry.settings")
    from django.core.management import execute_from_command_line

    # `python manage.py runserver` serves on port 3107 unless another port is given.
    if len(sys.argv) == 2 and sys.argv[1] == "runserver":
        sys.argv.append("0.0.0.0:3107")
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
