"""Allow ``python -m example_project <command>`` as a shortcut for ``example-manage``."""

from example_project.cli import manage

if __name__ == "__main__":
    manage()
